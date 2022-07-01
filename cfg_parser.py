from cfrais.parser import (
    strip, stripall, isa, are, assertare, explanation
)

from dataclasses import dataclass
import lark

@dataclass
class Number:
    value: int

@dataclass
class PMorAM:
    value: str

@dataclass
class Time:
    hour: int
    minute: int
    pmoram: str

@dataclass
class AlarmDay:
    value: str

@dataclass
class TimeDayHolder:
    time: Time
    day: object

@dataclass
class AlarmRequest:
    computer: bool
    voice: bool
    time: object
    time_interval: object

@dataclass
class TimeInterval:
    hour: int
    minute: int

@dataclass
class NumberList:
    values: object

@dataclass
class ProgramName:
    name: str

@dataclass
class RunProgram:
    name: str

@dataclass
class RecordRequest:
    pass

@dataclass
class ShortYes:
    value: str

@dataclass
class ShortNo:
    value: str

@dataclass
class ShortComputer:
    value: str

@dataclass
class ShortEndRecording:
    value: str

@dataclass
class ShortCancelRecording:
    value: str

@dataclass
class ShortPleaseRepeat:
    value: str

@dataclass
class ShortThanks:
    value: str

@dataclass
class ShortCruelAngels:
    value: str

__value = dict(
        OH=0,
        ZERO=0,
        ONE=1,
        TWO=2,
        THREE=3,
        FOUR=4,
        FIVE=5,
        SIX=6,
        SEVEN=7,
        EIGHT=8,
        NINE=9,
        TEN=10,
        ELEVEN=11,
        TWELVE=12,
        THIRTEEN=13,
        FOURTEEN=14,
        FIFTEEN=15,
        SIXTEEN=16,
        SEVENTEEN=17,
        EIGHTEEN=18,
        NINETEEN=19,
        TWENTY=20,
        THIRTY=30,
        FORTY=40,
        FIFTY=50,
        SIXTY=60,
        SEVENTY=70,
        EIGHTY=80,
        NINETY=90
)

def valuize(z):
    if isinstance(z, Number):
        return z
    return Number(__value[strip(z)])

class transformer(lark.Transformer):
    def alarm_request__pm_or_am(self, items):
        print("got", items)
        if are(items, ["A", "M"]):
            return PMorAM("AM")
        if are(items, ["P", "M"]):
            return PMorAM("PM")
        if are(items, ["AM"]):
            return PMorAM("AM")
        if are(items, ["PM"]):
            return PMorAM("PM")
        raise Exception()

    def alarm_request__ti_number_19(self, items):
        item, = items
        return valuize(item)

    def alarm_request__ti_number_12(self, items):
        item, = items
        return valuize(item)

    def alarm_request__ti_number_00(self, items):
        if len(items) == 1:
            item, = items
            return valuize(item)
        else:
            # like TWENTY Number(4) or something
            a, b = items
            return Number(valuize(a).value + valuize(b).value)

    def alarm_request__ti_number_oh0(self, items):
        return self.alarm_request__ti_number_00(items)

    def alarm_request__ti_time(self, items):
        print("got", items)
        # ti_time         ti_number_12 ti_number_oh0 pm_or_am
        if are(items, [Number, Number, PMorAM]):
            hour, minute, pmoram = items
            return Time(hour.value, minute.value, pmoram.value)

        # ti_time         ti_number_12 pm_or_am
        if are(items, [Number, PMorAM]):
            hour, pmoram = items
            return Time(hour.value, 0, pmoram.value)

        if are(items, [Number, "O'CLOCK", PMorAM]):
            hour, _, pmoram = items
            return Time(hour.value, 0, pmoram.value)


        raise Exception()

    def alarm_request__ti_day(self, items):
        item, = items
        return AlarmDay(strip(item))

    def alarm_request__time(self, items):
        # time            ti_day AT ti_time
        # time            ti_day ti_time
        # time            ti_time ti_day
        # time            ti_time ON ti_day
        # time            ti_time NEXT ti_day
        # time            ti_time
        time, = [z for z in items if isa(z, Time)]
        days = [z for z in items if isa(z, AlarmDay)]
        day = days[0] if len(days) > 0 else None
        return TimeDayHolder(time, day)

    def alarm_request__time_interval(self, items):
        # time_interval       ti_number_00 hour_or_hours
        # time_interval       ti_number_00 minute_or_minutes
        # time_interval       ti_number_00 hour_or_hours ti_number_00 minute_or_minutes
        # time_interval       ti_number_00 hour_or_hours AND ti_number_00 minute_or_minutes
        hours = 0
        minutes = 0
        if are(items, [Number, "hour_or_hours"]):
            hours = items[0].value
        elif are(items, [Number, "minute_or_minutes"]):
            minutes = items[0].value
        elif are(items, [Number, "hour_or_hours", Number, "minute_or_minutes"]):
            hours = items[0].value
            minutes = items[2].value
        elif are(items, [Number, "hour_or_hours", "AND", Number, "minute_or_minutes"]):
            hours = items[0].value
            minutes = items[3].value
        return TimeInterval(hours, minutes)


    def alarm_request(self, items):
        assertare(items, ["maybe_computer", "set_or_add", "maybe_voice", "REMINDER",
                          "for_to_in_on_at_nothing", "time_or_time_interval"])
        maybe_computer, set_or_add, maybe_voice, REMINDER, preposition_if_any, time_or_time_interval = items
        time = None
        time_interval = None
        that = time_or_time_interval.children[0]
        if isinstance(that, TimeDayHolder):
            time = that
        elif isinstance(that, TimeInterval):
            time_interval = that
        return AlarmRequest(
                computer = bool(maybe_computer.children),
                voice = bool(maybe_voice.children),
                time = time,
                time_interval = time_interval
        )

    def run__number_09(self, items):
        item, = items
        number = valuize(item)
        return NumberList([number.value])

    def run__numbers(self, items):
        if are(items, [NumberList, NumberList]):
            a, b = items
            return NumberList(a.values + b.values)
        assertare(items, [NumberList])
        item, = items
        return item

    def run__program_name(self, items):
        if are(items, ["greek_letter", NumberList]):
            greek_letter, numberlist = items
            greek_letter = strip(greek_letter.children[0]).lower()
            numberlist = "".join(str(z) for z in numberlist.values)
            return ProgramName(greek_letter + " " + numberlist)
        assertare(items, [Token])
        item, = items
        name = strip(item)
        pass
        pass
        return ProgramName(name.lower())

    def run(self, items):
        assertare(items, ["COMPUTER", "RUN", "PROGRAM", ProgramName])
        _, _, _, a = items
        return RunProgram(a.name)

    def short__yes(self, items):
        pass
        return ShortYes(stripall(items))

    def short__no(self, items):
        pass
        return ShortNo(stripall(items))

    def short__computer(self, items):
        pass
        return ShortComputer(stripall(items))

    def short__end_record(self, items):
        pass
        return ShortEndRecording(stripall(items))

    def short__cancel_record(self, items):
        pass
        return ShortCancelRecording(stripall(items))

    def short__please_repeat(self, items):
        pass
        return ShortPleaseRepeat(stripall(items))

    def short__thanks(self, items):
        pass
        return ShortThanks(stripall(items))

    def short__cruel_angels(self, items):
        pass
        return ShortCruelAngels(stripall(items))

    def short(self, items):
        item, = items
        return item

    def start(self, items):
        item, = items
        return item
