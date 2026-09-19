"""Тесты вспомогательных функций (без запуска GUI)."""

import pytest

import main


class TestFormatBytes:
    def test_bytes(self):
        assert main.format_bytes(500) == "500.0 B"

    def test_kilobytes(self):
        assert main.format_bytes(1024) == "1.0 KB"

    def test_megabytes(self):
        assert main.format_bytes(1024**2 * 5) == "5.0 MB"

    def test_gigabytes(self):
        assert main.format_bytes(1024**3 * 16) == "16.0 GB"

    def test_terabytes(self):
        assert main.format_bytes(1024**4 * 2) == "2.0 TB"

    def test_zero(self):
        assert main.format_bytes(0) == "0.0 B"


class TestFormatUptime:
    def test_seconds(self):
        assert main.format_uptime(42) == "0д 00:00:42"

    def test_minutes_hours(self):
        assert main.format_uptime(3600 + 120 + 3) == "0д 01:02:03"

    def test_days(self):
        assert main.format_uptime(86400 * 3 + 7200) == "3д 02:00:00"


class TestGpuInfo:
    def test_returns_list(self):
        assert isinstance(main.get_gpu_info(), list)

    def test_missing_gpututil(self, monkeypatch):
        monkeypatch.setattr(main, "GPUtil", None)
        assert main.get_gpu_info() == []


class TestTopProcesses:
    def test_memory_top(self):
        procs = main.get_top_processes(limit=5)
        assert len(procs) <= 5
        # Список отсортирован по убыванию памяти
        values = [p[1] for p in procs]
        assert values == sorted(values, reverse=True)

    def test_limit_zero(self):
        assert main.get_top_processes(limit=0) == []


class TestHtmlReport:
    def test_report_is_valid_html(self):
        report = main.build_html_report()
        assert report.startswith("<!DOCTYPE html>")
        assert "</html>" in report
        assert "Система" in report
        assert "Диски" in report
