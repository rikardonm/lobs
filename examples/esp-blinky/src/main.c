#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "sdkconfig.h"


void app_main(void)
{
    const gpio_num_t _led_io = 13;
    uint8_t _led_state = true;

    gpio_reset_pin(_led_io);
    gpio_set_direction(_led_io, GPIO_MODE_OUTPUT);

    while (true) {
        gpio_set_level(_led_io, _led_state);
        _led_state = !_led_state;
        vTaskDelay(500 / portTICK_PERIOD_MS);
    }
}
