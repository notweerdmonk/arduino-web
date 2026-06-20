#ifndef ALARM_HPP
#define ALARM_HPP

struct Medicine {
  uint8_t     dayOfMonth;
  uint8_t     dayOfWeek;
  uint8_t     hour;
  uint8_t     decade;
  const char* text;
};

const Medicine medicines[] = {
  {0, 1, 8, 3, "Ibup"},
  {0, 3, 20, 0, "PaRa"},
};

#define N_MED  (sizeof(medicines) / sizeof(medicines[0]))

#endif  // ALARM_HPP
