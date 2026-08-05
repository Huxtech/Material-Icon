from kvdroid.jclass.android import WindowManagerLayoutParams
from kvdroid import activity
from android.runnable import run_on_ui_thread


@run_on_ui_thread
def set_soft_input_adjust_nothing():
    window = activity.getWindow()
    window.setSoftInputMode(WindowManagerLayoutParams().SOFT_INPUT_ADJUST_NOTHING)

