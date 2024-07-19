```cpp
inline bool PrepareHDMapUpdateRequest(std::shared_ptr<nio::ad::messages::HDMapUpdateRequest>& message_ptr) {
    message_ptr->set_uuid("example-uuid");
    message_ptr->set_priority(1);
    message_ptr->set_timestamp(1234567890);
    message_ptr->set_expiration_time(9876543210);
    message_ptr->set_socid(1001);
    message_ptr->set_hdmap_version(2002);
    message_ptr->set_tile_id(3003);
    message_ptr->set_format_version(4004);
    message_ptr->set_current_tile_version(5005);
    message_ptr->mutable_sensor_original_ts()->set_sensor_id(6006);
    message_ptr->set_publish_ptp_ts(7007);
    message_ptr->set_publisher_id("example-publisher");
    message_ptr->set_counter(8008);
    message_ptr->set_publish_ts(9009);
    return true;
}
```

