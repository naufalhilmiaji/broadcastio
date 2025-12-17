# Broadcastio Unit Testing

## Check Lists
- [x] Wrong host path validation\
    It returns:
    ```
    ERROR:__main__:broadcastio error
    Traceback (most recent call last):
    File "C:\Users\pcom\Documents\Development\Projects\Personal\broadcastio\python\run_test.py", line 42, in <module>
        result = orch.send(msg_attachment)
                ^^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\Users\pcom\Documents\Development\Projects\Personal\broadcastio\python\broadcastio\core\orchestrator.py", line 53, in send
        self._validate_message(message)
    File "C:\Users\pcom\Documents\Development\Projects\Personal\broadcastio\python\broadcastio\core\orchestrator.py", line 39, in _validate_message
        raise AttachmentError(
    broadcastio.core.exceptions.AttachmentError: Attachment not found: shareed_files/DailyReport-15-December-2025.xlsx
    ```

- [x] Wrong provider path validation
  In Python returns:
  ```
  DeliveryResult(success=False, provider='none', message_id=None, error=DeliveryError(code='PROVIDER_UNAVAILABLE', message='whatsapp service unavailable', details={'exception': '500 Server Error: Internal Server Error for url: http://localhost:3000/send'}))
  ```
  In Node returns:
  ```
  {"error":"Attachment not found: /app/sharexd_files/DailyReport-15-December-2025.xlsx","level":"error","message":"Send failed","timestamp":"2025-12-16T07:49:41.329Z"}
  ```

- [x] Node service down
  It returns:
  ```
  DeliveryResult(success=False, provider='none', message_id=None, error=DeliveryError(code='PROVIDER_UNAVAILABLE', message='whatsapp service unavailable', details={'exception': 'HTTPConnectionPool(host=\'localhost\', port=3000): Max retries exceeded with url: /send (Caused by NewConnectionError("HTTPConnection(host=\'localhost\', port=3000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it"))'}))
  ```

- [x] WhatsApp logical fail
  It returns:
  ```
  DeliveryResult(success=False, provider='none', message_id=None, error=DeliveryError(code='WHATSAPP_REJECTED', message='Forced logical failure for testing', details=None))
  ```



