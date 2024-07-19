```cpp
inline bool PrepareDataTriggeredReq(std::shared_ptr<nio::ad::messages::DataTriggeredReq>& message_ptr) {
    message_ptr->set_flag(true);
    message_ptr->set_triggered_event("example_event");
    message_ptr->set_uuid_num("example_uuid");
    message_ptr->set_trigger_payload("example_payload");
    message_ptr->mutable_sensor_original_ts()->set_field_name("example_value"); // Assuming SensorTSHeader has a set_field_name method
    message_ptr->set_publish_ptp_ts(123456789);
    message_ptr->set_publisher_id("example_publisher");
    message_ptr->set_counter(987654321);
    message_ptr->set_publish_ts(1234567890);
    return true;
}
```

