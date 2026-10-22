# Kalmeijer Pico W OTA test releases

The Pico downloads the signed `version.json`, then the immutable application file named in that manifest. This test repository is public.

Release 1.0.7 contains the Kalmeijer control application with PLC acknowledgement/retry handling, a read-only communication heartbeat, and the existing shared-watchdog/trial health hooks. It is an application update, not a complete initial Pico installation or firmware image.

The Pico must first have the GitHub-pull supervisor, compatible ROM/drivers, its local hotspot credentials and matching release-verification key installed over USB. Customer updates then need only the configured hotspot and the established Stop-button/PLC-CPU-STOP startup sequence. No PC uploader is required at the customer site.

Never publish `ota_config.py`, `PICO_OTA_KEY`, live settings, or Wi-Fi passwords. A manifest signature is public; the signing key remains private. Only appropriately signed releases are accepted.

`app.py` is the earlier LED demo and is retained for history. The new signed manifest points to the control application's content-addressed file under `applications/`; the GitHub-pull updater rejects the old demo manifest format.

Publish each immutable application asset before (or in the same commit as) its matching manifest. Release counters must strictly increase. Device trial execution and confirmation are still required; downloading and staging a release does not prove hardware compatibility.
