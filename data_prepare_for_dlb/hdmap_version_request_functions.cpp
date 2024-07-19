```cpp
inline bool PrepareHDMapVersionRequest(std::shared_ptr<nio::ad::messages::HDMapVersionRequest>& message_ptr) {
    message_ptr = std::make_shared<nio::ad::messages::HDMapVersionRequest>();
    message_ptr->set_uuid("example-uuid");
    message_ptr->set_format_version(1);
    message_ptr->set_hdmap_version(2);
    message_ptr->set_tile_ids("example-tile-ids");
    auto sensor_original_ts = message_ptr->mutable_sensor_original_ts();
    sensor_original_ts->set_timestamp(3);
    message_ptr->set_publish_ptp_ts(4);
    message_ptr->set_publisher_id("example-publisher-id");
    message_ptr->set_counter(5);
    message_ptr->set_publish_ts(6);
    return true;
}
```

