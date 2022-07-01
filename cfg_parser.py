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
class ShortRequestRecord:
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

class transformer(lark.Transformer):
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

    def short__request_record(self, items):
        return ShortRequestRecord()

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

def is_cancel_recording(what):
    return isinstance(what, ShortCancelRecording)


def is_end_recording(what):
    return isinstance(what, ShortEndRecording)
