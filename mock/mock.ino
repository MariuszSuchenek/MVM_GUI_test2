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

namespace mvm {

struct Seconds
{
  static
  unsigned long from_millis(unsigned long milli)
  {
    return milli / 1000ul;
  }

  static
  unsigned long from_micros(unsigned long micro)
  {
    return micro / 1000000ul;
  }
};

template<class Time>
unsigned long now()
{
  return Time::from_micros(micros());
}

size_t send(Stream& connection, String const& data)
{
  auto const header = String("valore=");
  auto const len = header.length() + data.length();

  auto sent = connection.print(header);

  auto pos = data.c_str();

  while (sent != len) {
    auto const to_be_sent = len - sent;
    auto const nbytes
      = to_be_sent > SERIAL_TX_BUFFER_SIZE
      ? SERIAL_TX_BUFFER_SIZE
      : to_be_sent;

    auto const written = connection.write(pos, nbytes);
    pos += written;
    sent += written;
  }

  sent += connection.println("");

  return sent;
}

} // ns mvm

unsigned long pause_lg_expiration = mvm::now<mvm::Seconds>() + 10;

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

  parameters["run"]    = String(0);
  parameters["mode"]   = String(0);
  parameters["backup"] = String(0);

  parameters["pcv_trigger"]        = String(5);
  parameters["pcv_trigger_enable"] = String(0);

  parameters["rate"]             = String(12);
  parameters["ratio"]            = String(2);
  parameters["ptarget"]          = String(15);
  parameters["assist_ptrigger"]  = String(1);
  parameters["assist_flow_min"]  = String(20);
  parameters["pressure_support"] = String(10);
  parameters["backup_enable"]    = String(1);
  parameters["backup_min_time"]  = String(10);
  parameters["pause_lg_time"]    = String(10);
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

  if (name == "pause_lg" && value == "1") {
    pause_lg_expiration
    = mvm::now<mvm::Seconds>()
    + parameters["pause_lg_time"].toInt();
  }

  return "OK";
}

String get(String const& command)
{
  auto const name = parse_word(command);

  if (name == "all") {
    return
        String(random(20, 70))     + "," // pressure
      + String(random(3, 21))      + "," // flow
      + String(random(30, 100))    + "," // o2
      + String(random(6, 8))       + "," // bpm
      + String(random(1000, 1500)) + "," // tidal
      + String(random(4, 20))      + "," // peep
      + String(random(10, 50))     + "," // temperature
      + String(random(0, 1))       + "," // power_mode
      + String(random(20, 100))    + "," // battery
      + String(random(70, 80))     + "," // peak
      + String(random(1000, 2000)) + "," // total_inspired_volume
      + String(random(1000, 2000)) + "," // total_expired_volume
      + String(random(10, 100));         // volume_minute
  } else if (name == "pause_lg_time") {
    auto const now = mvm::now<mvm::Seconds>();
    return now > pause_lg_expiration ? "0" : String(pause_lg_expiration - now);
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
      mvm::send(connection, get(command));
    } else if (command_type == "set") {
      mvm::send(connection, set(command));
    } else {
      mvm::send(connection, "notok");
    }
  }
}

void loop()
{
  serial_loop(Serial);
  serial_loop(Debug);
}
