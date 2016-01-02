// #include <string>
#ifdef __cplusplus
extern "C" {
#endif

    typedef struct Reading{
        unsigned long node_id;
        unsigned long sensor_id;
        double value;
        char* timestamp;
    } Reading;

    void append_reading_to_buffer(char *buf, struct Reading *r);


#ifdef __cplusplus
}
#endif
