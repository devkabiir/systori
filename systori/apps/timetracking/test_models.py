import json
from datetime import timedelta, datetime

from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from freezegun import freeze_time

from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from .models import Timer


NOW = timezone.now().replace(hour=12)


class TimerTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company)

    def test_launch(self):
        timer = Timer.launch(self.user)
        self.assertTrue(timer.pk)
        self.assertEqual(timer.user, self.user)
        self.assertTrue(timer.is_running)

    def test_launch_with_kwargs(self):
        timer = Timer.launch(self.user, latitude=52.5076, longitude=13.3904)
        self.assertTrue(timer.pk)
        self.assertEqual(timer.user, self.user)
        self.assertEqual(timer.latitude, 52.5076)
        self.assertEqual(timer.longitude, 13.3904)
        self.assertTrue(timer.is_running)

    def test_no_two_timers(self):
        Timer.launch(self.user)
        with self.assertRaises(ValidationError):
            Timer.launch(self.user)

    def test_get_duration(self):
        timer = Timer.launch(self.user)
        self.assertEqual(
            timer.get_duration(now=timezone.now() + timedelta(hours=4)),
            [4, 0, 0]
        )

    def test_stop(self):
        timer = Timer.launch(self.user)
        timer.stop(ignore_short_duration=False)
        self.assertTrue(timer.end)

    def test_stop_zero_timer_ignores_it(self):
        timer = Timer.launch(self.user)
        timer.stop()
        self.assertFalse(Timer.objects.filter(pk=timer.pk).exists())

    def test_to_dict(self):
        timer = Timer.launch(self.user)
        self.assertEqual(
            timer.to_dict(),
            {'duration': timer.get_duration()}
        )

    @freeze_time(NOW)
    def test_save_regular_timer(self):
        # Regular timer
        timer = Timer(user=self.user)
        timer.save()
        self.assertEqual(timer.start, NOW)
        self.assertEqual(timer.date, NOW.date())
        self.assertIsNone(timer.end)

        with self.assertRaises(ValidationError):
            timer = Timer(user=self.user)
            timer.save()

    @freeze_time(NOW)
    def test_save_with_end(self):
        timer = Timer(user=self.user, end=NOW + timedelta(hours=2))
        timer.save()
        self.assertEqual(timer.start, NOW)
        self.assertEqual(timer.date, NOW.date())
        self.assertEqual(timer.duration, 60 * 60 * 2)

    @freeze_time(NOW)
    def test_save_with_duration(self):
        timer = Timer(user=self.user, duration=60 * 60 * 2)
        timer.save()
        self.assertEqual(timer.start, NOW)
        self.assertEqual(timer.date, NOW.date())
        self.assertEqual(timer.end, NOW + timedelta(hours=2))

    @freeze_time(NOW)
    def test_save_correction_timer(self):
        timer = Timer(user=self.user, duration=60 * 60 * 2, kind=Timer.CORRECTION)
        timer.save()
        self.assertIsNone(timer.start)
        self.assertIsNone(timer.end)
        self.assertEqual(timer.date, NOW.date())

    @freeze_time(NOW)
    def test_save_overlapping_timer(self):
        Timer.objects.create(
            user=self.user,
            start=NOW - timedelta(hours=2), end=NOW + timedelta(hours=2),
            kind=Timer.HOLIDAY)
        timer = Timer(
            user=self.user,
            start=NOW - timedelta(hours=1), end=NOW + timedelta(hours=5),
            kind=Timer.HOLIDAY)
        with self.assertRaises(ValidationError):
            timer.save()


class TimerQuerySetTest(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company)
        self.user2 = UserFactory(company=self.company)

    def test_filter_date(self):
        now = timezone.now().replace(hour=9)
        yesterday = now - timedelta(days=1)
        Timer.objects.create(
            user=self.user,
            start=yesterday,
            end=yesterday + timedelta(hours=8)
        )

        timer = Timer(user=self.user, duration=60 * 60 * 2)
        timer.save()
        self.assertEqual(
            Timer.objects.filter_date().get(),
            Timer.objects.get(pk=timer.pk)
        )

    def test_filter_running(self):
        now = timezone.now().replace(hour=9)
        yesterday = now - timedelta(days=1)
        Timer.objects.create(
            user=self.user,
            start=yesterday,
            end=yesterday + timedelta(hours=8)
        )
        Timer.objects.create(
            user=self.user,
            duration=3600,
            kind=Timer.CORRECTION
        )
        self.assertFalse(Timer.objects.filter_running().exists())

        timer = Timer.launch(self.user)
        self.assertEqual(
            Timer.objects.filter_running().get(),
            Timer.objects.get(pk=timer.pk)
        )

    def test_create_batch(self):
        now = timezone.now()
        start = now.replace(hour=7, minute=0, second=0, microsecond=0)
        result = Timer.objects.create_batch(
            user=self.user, days=3, start=now,
            kind=Timer.HOLIDAY, comment='Test comment'
        )
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].start, start)
        self.assertEqual(result[0].end, start + timedelta(seconds=Timer.WORK_HOURS))
        self.assertEqual(result[0].kind, Timer.HOLIDAY)
        self.assertEqual(result[0].comment, 'Test comment')
        self.assertEqual(result[1].start, start + timedelta(days=1))
        self.assertEqual(result[1].end, start + timedelta(days=1) + timedelta(seconds=Timer.WORK_HOURS))
        self.assertEqual(result[2].start, start + timedelta(days=2))
        self.assertEqual(result[2].end, start + timedelta(days=2) + timedelta(seconds=Timer.WORK_HOURS))
