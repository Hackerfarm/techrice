#include "utilsawesome.h"
/*
 *    Concatenates the information from one Reading to the tx_buf
 *
 *    The format of one reading string is:
 *        reading->name:reading->value:reading->timestamp;
 *
 *    With real information coming from sensors should look like:
 *        "distance:205.00:5623;"
 *
 *    When many Readings have been attached having called this function several times
 *      this is how the tx_buf looks like:
 *        "distance:205.00:18323;temperature:24.00:18323;humidity:45.10:1832"
 *
 */

//void append_reading(char *buf, struct Reading *r){
//    char size = sizeof(r);
//    char tmp[size];
//    memset(tmp, 0, size);
//    sprintf(buf, "%u,%u,%%u", r->node_id, r->sensor_id, r->timestamp);
//    char tmp2[10];
//    memset(tmp2, 0, 10);
//    char *current_value = dtostrf(reading->value, 2, 2, (char *)tmp2);
//    strcat(buf, current_value);
////    strcat((char*) buf, tmp2);
//}

void append_reading_to_buffer(char *tx_buf, struct Reading *reading)
{
    char tmp[20];
    char buf[20];
    char str[80];
    
    strcpy(str, "");
    
    memset(tmp, 0, 20);
    sprintf(tmp, "%u", reading->node_id);
    strcat(str, tmp);
    strcat(str, ",");
//
    memset(tmp, 0, 20);
    sprintf(tmp, "%u", reading->sensor_id);
    strcat(str, tmp);
    strcat(str, ",");
    
    memset(tmp, 0, 20);
    char *current_value = dtostrf(reading->value, 2, 2, tmp);
    strcat(str, current_value);
    strcat(str, ",");
    
    //memset(tmp, 0, 20);
    //sprintf(tmp, "%u", reading->timestamp);
    strcat(str, reading->timestamp);
    strcat(str, ";");
    strcat(str, "\0");
    strcat((char *)tx_buf,(char *) str);
}