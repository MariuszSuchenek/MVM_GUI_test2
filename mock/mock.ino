#include <StandardCplusplus.h>

// If this fails, install ArduinoSTL from the Arduino library
// and use the following instead:
// #include <ArduinoSTL.h>

#include <map>
#include <vector>
#include <algorithm> // std::find
#include <SoftwareSerial.h>

SoftwareSerial Debug(2, 3); // RX, TX

// change it to \n in case of line termination is not \n\r
auto const terminator = '\r';
auto const separator = ' ';

std::map<String, String> parameters;

std::vector<String> random_measures;

void setup()
{
  Serial.begin(115200);
  while (!Serial);
  Serial.setTimeout(50000);
  Debug.begin(115200);

  random_measures = { "pressure", "bpm", "flow", "o2", "tidal", "peep",
                      "temperature", "power_mode", "battery" };

  parameters["alarm"] = String(0);
  parameters["warning"] = String(0);
}

// this is tricky, didn't had the time to think a better algo
String parse_word(String const& command)
{
  auto const first_sep_pos = command.indexOf(separator);
  if (first_sep_pos == -1) {
    return command;
  }

  auto const second_sep_pos = command.indexOf(separator, first_sep_pos + 1);

  return command.substring(first_sep_pos + 1, second_sep_pos);
}

String set(String const& command)
{
  auto const name = parse_word(command);
  auto const value = parse_word(command.substring(name.length() + 4));
  parameters[name] = value;
  return "OK";
}

String get(String const& command)
{
  auto const name = parse_word(command);

  if (name == "all") {
    return
        String(random(10, 79))     + "," // pressure
      + String(random(3, 21))      + "," // flow
      + String(random(10, 100))    + "," // o2
      + String(random(12, 20))     + "," // bpm
      + String(random(1000, 1500)) + "," // tidal
      + String(random(4, 20))      + "," // peep
      + String(random(10, 50))     + "," // temperature
      + String(random(0, 1))       + "," // power_mode
      + String(random(1, 100))     + "," // battery
      + String(random(70, 80))     + "," // peak
      + String(random(1000, 2000)  + "," // total_inspired_volume
      + String(random(1000, 2000)  + "," // total_expired_volume
      + String(random(10, 100));         // volume_minute
  }

  auto const it = std::find(
      random_measures.begin()
    , random_measures.end()
    , name
  );

  if (it != random_measures.end()) {
    return String(random(10, 100));
  } else {
    auto const it = parameters.find(name);

    return it == parameters.end() ? String("unknown") : it->second;
  }
}

void serial_loop(Stream& connection)
{
  if (connection.available() > 0) {
    String command = connection.readStringUntil(terminator);
    command.trim();
    auto const command_type = command.substring(0, 3);

    if (command.length() == 0) {
    } else if (command_type == "get") {
      connection.println("valore=" + get(command));
    } else if (command_type == "set") {
      connection.println("valore=" + set(command));
    } else {
      connection.println("valore=notok");
    }
  }
}

void serial()
{
  serial_loop(Serial);
  serial_loop(Debug);
}
