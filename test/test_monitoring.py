from algorunner.hooks import Hook
from unittest.mock import patch

from algorunner.monitoring import Timer

def test_timer_returns_duration_in_ms():
    with patch('algorunner.monitoring.time') as time_mock:
        time_mock.side_effect = [2, 3]

        t = Timer()
        with t:
            pass

        assert t.ms() == 1000

def test_timer_bubbles_exceptions():
    have_exc = False

    with patch('algorunner.monitoring.logger') as logger_mock:
        try:
            t = Timer()
            with t:
                raise Exception()
        except Exception:
            have_exc = True
        
        assert logger_mock.error.call_count == 1    
    assert have_exc

def test_timer_triggers_hooks():
    with patch('algorunner.monitoring.hook') as hook_mock:
        with patch('algorunner.monitoring.time') as time_mock:
            time_mock.side_effect = [2.3, 3.0]

            t = Timer(Hook.PROCESS_DURATION)
            with t:
                pass

            assert t.ms() == 700
            hook_mock.assert_called_once_with(Hook.PROCESS_DURATION, t.ms())
