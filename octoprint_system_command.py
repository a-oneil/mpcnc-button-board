import sys, cnc_button_board

ha = cnc_button_board.HomeAssistant()
arg = sys.argv[1]

try:
  # Toggle CNC E-Stop
  # OCTO5
  if arg == "cncestop":
    ha.toggle_switch("cnc_estop")
    cnc_button_board.post_message("Toggling CNC E-STOP")

  # Toggle Vacuum
  # OCTO6
  elif arg == "vacuum":
    ha.toggle_switch("garage_vacuum")
    cnc_button_board.post_message("Toggling Vacuum")

  # Toggle Lights
  # OCTO7
  elif arg == "lights":
    ha.toggle_switch("garage_vacuum")
    cnc_button_board.post_message("Toggling Lights")

  # Toggle Fan
  # OCTO8
  elif arg == "fan":
    ha.toggle_switch("cnc_lights")
    cnc_button_board.post_message("Toggling Fan")

  # Turn Fan ON
  # OCTO1
  elif arg == "fanon":
    ha.turn_on_switch("garage_fan")
    cnc_button_board.post_message("Turning Garage Fan On")

  # Turn Fan Off
  # OCTO2
  elif arg == "fanoff":
    ha.turn_off_switch("garage_fan")
    cnc_button_board.post_message("Turning Garage Fan Off")

  # Turn Vacuum ON
  # OCTO03
  elif arg == "vacuumon":
    ha.turn_on_switch("garage_vacuum")
    cnc_button_board.post_message("Turning Garage Vacuum On")

  # Turn Vacuum Off
  # OCTO04
  elif arg == "vacuumoff":
    ha.turn_off_switch("garage_vacuum")
    cnc_button_board.post_message("Toggling Garage Vacuum Off")

  # Tool Change Required
  # OCTO100
  elif arg == "toolchange":
    cnc_button_board.post_message("The CNC has paused for a tool change!")

  # CNC Finished Notification
  # OCTO200
  elif arg == "cnccomplete":
    ha.turn_off_switch("garage_fan")
    cnc_button_board.post_message("CNC Program Complete")
except:
  print("Bad Input Argument")