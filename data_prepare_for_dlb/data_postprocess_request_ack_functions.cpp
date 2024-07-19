```cpp
inline bool PrepareDataPostprocessReqAck(std::shared_ptr<nio::ad::messages::DataPostprocessReqAck>& message_ptr) {
    message_ptr = std::make_shared<nio::ad::messages::DataPostprocessReqAck>();
    message_ptr->set_accept(nio::ad::messages::Postprocess_BUSY);
    return true;
}
```

