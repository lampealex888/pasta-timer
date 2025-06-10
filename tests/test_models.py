from models import PastaInfo, TimerEvent

def test_pasta_info_time_range():
    pasta = PastaInfo('spaghetti', 8, 10)
    assert pasta.time_range == (8, 10)

def test_pasta_info_is_valid_time():
    pasta = PastaInfo('spaghetti', 8, 10)
    assert pasta.is_valid_time(8)
    assert pasta.is_valid_time(9)
    assert pasta.is_valid_time(10)
    assert not pasta.is_valid_time(7)
    assert not pasta.is_valid_time(11)

def test_pasta_info_increment_usage():
    pasta = PastaInfo('spaghetti', 8, 10)
    assert pasta.usage_count == 0
    pasta.increment_usage()
    assert pasta.usage_count == 1

def test_timer_event_minutes_seconds():
    event = TimerEvent('tick', 125, 'spaghetti')
    assert event.minutes == 2
    assert event.seconds == 5 