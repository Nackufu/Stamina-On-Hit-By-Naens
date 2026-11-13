; Compile-only interface declarations; never install or compile these into runtime PEX.
Scriptname SKI_ConfigBase extends SKI_QuestBase Hidden
String Property ModName
 String Function Get() Native
 Function Set(String value) Native
EndProperty
String[] Property Pages
 String[] Function Get() Native
 Function Set(String[] value) Native
EndProperty
Function SetCursorPosition(Int a_position) Native
Function SetCursorFillMode(Int a_fillMode) Native
Int Function AddHeaderOption(String a_text, Int a_flags = 0) Native
Int Function AddToggleOption(String a_text, Bool a_checked, Int a_flags = 0) Native
Int Function AddSliderOption(String a_text, Float a_value, String a_formatString = "{0}", Int a_flags = 0) Native
Function SetToggleOptionValue(Int a_option, Bool a_checked, Bool a_noUpdate = False) Native
Function SetSliderOptionValue(Int a_option, Float a_value, String a_formatString = "{0}", Bool a_noUpdate = False) Native
Function SetInfoText(String a_text) Native
Function SetSliderDialogStartValue(Float a_value) Native
Function SetSliderDialogDefaultValue(Float a_value) Native
Function SetSliderDialogRange(Float a_minValue, Float a_maxValue) Native
Function SetSliderDialogInterval(Float a_value) Native
