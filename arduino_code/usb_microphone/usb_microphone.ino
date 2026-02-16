#define EIDSP_QUANTIZE_FILTERBANK 0

#include <PDM.h>
#include <Karthikeyan2kk-project-1_inferencing.h>

/** ===== Inference buffer structure ===== */
typedef struct {
    int16_t *buffer;
    uint8_t buf_ready;
    uint32_t buf_count;
    uint32_t n_samples;
} inference_t;

static inference_t inference;
static signed short sampleBuffer[2048];
static bool debug_nn = false;

static bool system_running = false;

/* -------------------- SETUP -------------------- */
void setup() {
    Serial.begin(115200);
    while (!Serial);

    Serial.println("=== Cough Detection System ===");
    Serial.println("Commands:");
    Serial.println("  r → Start");
    Serial.println("  s → Stop");

    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);

    if (!microphone_inference_start(EI_CLASSIFIER_RAW_SAMPLE_COUNT)) {
        ei_printf("ERR: Audio buffer allocation failed\n");
        while (1);
    }
}

/* -------------------- LOOP -------------------- */
void loop() {

    /** ✅ SERIAL COMMANDS */
    if (Serial.available()) {
        char cmd = Serial.read();

        if (cmd == 'r') {
            system_running = true;
            Serial.println("[SYSTEM] STARTED");
        }

        if (cmd == 's') {
            system_running = false;
            digitalWrite(LED_BUILTIN, LOW);
            Serial.println("[SYSTEM] STOPPED");
        }
    }

    if (!system_running) {
        delay(100);
        return;
    }

    ei_printf("Recording...\n");

    if (!microphone_inference_record()) {
        ei_printf("ERR: Recording failed\n");
        return;
    }

    signal_t signal;
    signal.total_length = EI_CLASSIFIER_RAW_SAMPLE_COUNT;
    signal.get_data = &microphone_audio_signal_get_data;

    ei_impulse_result_t result = { 0 };

    EI_IMPULSE_ERROR r = run_classifier(&signal, &result, debug_nn);
    if (r != EI_IMPULSE_OK) {
        ei_printf("ERR: Classification failed (%d)\n", r);
        return;
    }

    float cough_value = 0.0;

    for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {

        ei_printf("%s: %.5f\n",
                  result.classification[ix].label,
                  result.classification[ix].value);

        if (strcmp(result.classification[ix].label, "cough") == 0) {
            cough_value = result.classification[ix].value;
        }
    }

    /** ⭐ COUGH THRESHOLD ⭐ */
    if (cough_value >= 0.60) {
        digitalWrite(LED_BUILTIN, HIGH);
        Serial.println("COUGH_DETECTED");
    } 
    else {
        digitalWrite(LED_BUILTIN, LOW);
    }

    delay(200);
}

/* -------------------- PDM CALLBACK -------------------- */
static void pdm_data_ready_inference_callback(void) {

    int bytesAvailable = PDM.available();
    int bytesRead = PDM.read((char *)&sampleBuffer[0], bytesAvailable);

    if (inference.buf_ready == 0) {
        for (int i = 0; i < bytesRead >> 1; i++) {

            inference.buffer[inference.buf_count++] = sampleBuffer[i];

            if (inference.buf_count >= inference.n_samples) {
                inference.buf_count = 0;
                inference.buf_ready = 1;
                break;
            }
        }
    }
}

/* -------------------- MIC START -------------------- */
static bool microphone_inference_start(uint32_t n_samples) {

    inference.buffer = (int16_t *)malloc(n_samples * sizeof(int16_t));
    if (!inference.buffer) return false;

    inference.buf_count = 0;
    inference.n_samples = n_samples;
    inference.buf_ready = 0;

    PDM.onReceive(&pdm_data_ready_inference_callback);
    PDM.setBufferSize(4096);

    if (!PDM.begin(1, EI_CLASSIFIER_FREQUENCY)) {
        ei_printf("ERR: PDM start failed\n");
        microphone_inference_end();
        return false;
    }

    PDM.setGain(127);
    return true;
}

/* -------------------- MIC RECORD -------------------- */
static bool microphone_inference_record(void) {

    inference.buf_ready = 0;
    inference.buf_count = 0;

    while (!inference.buf_ready) {
        delay(10);
    }
    return true;
}

/* -------------------- GET AUDIO DATA -------------------- */
static int microphone_audio_signal_get_data(size_t offset, size_t length, float *out_ptr) {

    numpy::int16_to_float(&inference.buffer[offset], out_ptr, length);
    return 0;
}

/* -------------------- MIC END -------------------- */
static void microphone_inference_end(void) {
    PDM.end();
    free(inference.buffer);
}

#if !defined(EI_CLASSIFIER_SENSOR) || EI_CLASSIFIER_SENSOR != EI_CLASSIFIER_SENSOR_MICROPHONE
#error "Invalid model for microphone"
#endif