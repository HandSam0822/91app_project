from nis import match
from django.shortcuts import render

WARNING = "#dc143c"
FREEPUSH = "#fff8dc"
OPERATE = "#3cb371"
# need to add some attributes to change color
def calculator_action(request):
    try:
        # GET REQUEST operation
        if request.method == "GET":
            context = initial_context()
            return render(request, "calculator/calculator.html", context)

        # POST REQUEST operation
        input = process_parameters(request.POST)

        if input["button"].isdigit():
            context = process_digit(input)
        else:
            context = process_operation(input)

        return render(request, "calculator/calculator.html", context)
    except Exception as e:
        return render(request, "calculator/error.html", {"error": str(e)})


def initial_context():
    context = {
        "hi": 0,
        "mid": 0,
        "lo": 0,
        "out": 0,
        "entering": True,
        "cnt": 1,
        "bg_color": FREEPUSH,
    }
    return context


def process_parameters(request):

    missing_param = check_missing_param(request)
    if missing_param:
        return missing_param
    invalid_param = check_invalid_param(request)
    if invalid_param:
        return invalid_param

    return {
        "button": request["button"],
        "hi": int(request["hi"]),
        "mid": int(request["mid"]),
        "lo": int(request["lo"]),
        "entering": request["entering"],
        "cnt": int(request["cnt"]),
    }


def check_missing_param(request):
    if (
        "button" not in request
        or "hi" not in request
        or "mid" not in request
        or "lo" not in request
        or "entering" not in request
        or "cnt" not in request
    ):
        raise Exception("missing parameters")


def check_invalid_param(request):
    # check button is within 0-9 and is valid operator
    button = request["button"]

    if button.isdigit():
        if int(button) < 0 or int(button) > 9:
            raise Exception("button: " + button + " is not between 0-9")

    else:
        if (
            button != "plus"
            and button != "minus"
            and button != "times"
            and button != "divide"
            and button != "push"
        ):
            raise Exception("button: " + button + " is not + - * / push")

    # check hi, mid, lo is valid number, lstrip('-') is to make negative number also pass isdigit()
    hi, mid, lo = (
        request["hi"].lstrip("-"),
        request["mid"].lstrip("-"),
        request["lo"].lstrip("-"),
    )
    if not hi.isdigit() or not mid.isdigit() or not lo.isdigit():
        raise Exception("hi/mid/lo is not valid digit")

    # check entering is either True or False
    entering = request["entering"]
    if entering != "True" and entering != "False":
        raise Exception("entering is not True or False")

    # check cnt is a valid number
    cnt = request["cnt"]
    if not cnt.isdigit():
        raise Exception("cnt: " + cnt + "is not valid number")


def process_digit(input):
    hi, mid, button, entering, cnt = (
        input["hi"],
        input["mid"],
        int(input["button"]),
        input["entering"],
        int(input["cnt"]),
    )

    if entering == "True":
        new_hi = hi * 10 + button
        input["hi"] = new_hi

    else:
        input["hi"] = button
        input["mid"] = hi
        input["lo"] = mid
        input["entering"] = True
        input["cnt"] = cnt + 1
    input["out"] = input["hi"]
    print(input)
    return input


def process_operation(input):
    hi, mid, lo, oper, cnt = (
        input["hi"],
        input["mid"],
        input["lo"],
        input["button"],
        input["cnt"],
    )
    if oper == "push":
        if cnt == 3:
            raise Exception("stack overflow")
        else:
            input["hi"] = 0
            input["mid"] = hi
            input["lo"] = mid
            input["bg_color"] = FREEPUSH
            input["cnt"] = cnt + 1

    else:
        if cnt == 1:
            raise Exception("stack underflow")
        if hi == 0:
            raise Exception("divide by zero")

        res = calculate(oper, mid, hi)
        input["hi"] = res
        input["mid"] = lo
        input["lo"] = 0
        input["bg_color"] = OPERATE
        input["cnt"] = cnt - 1
        input["entering"] = False

    input["out"] = input["hi"]
    print(input)
    return input


def calculate(oper, mid, hi):
    if oper == "plus":
        return mid + hi
    elif oper == "minus":
        return mid - hi
    elif oper == "times":
        return mid * hi
    elif oper == "divide":
        return mid // hi
    else:
        return None
