# ITU AI CCTV - Internal Face Recognition Notes

Face recognition is optional, internal, privacy-gated, and not high-security identity proof.

## Current State

- OpenCV LBPH backend is deployed for approved internal testing.
- Production can enable the backend through private `.env`.
- The approved internal test label `BURN` has been enrolled with private local samples.
- The test enrollment was improved from 3 samples to 6 samples using private CCTV-derived crops.
- Some CCTV-derived samples were rejected because face detection or quality was not suitable.

Do not include private sample filenames, generated crop filenames, enrollment images, embeddings, or model contents in public docs or Git.

## Recognition Limits

Recognition depends on:

- face readiness
- face angle
- lighting
- blur
- distance from camera
- camera resolution
- how closely live evidence matches enrolled samples

`UNKNOWN` means no reliable internal match. It does not mean suspicious.

## Privacy Rules

- Use only approved internal reference images.
- Keep reference images, embeddings, and models local/private.
- Never commit face enrollment images, embeddings, or model files.
- Do not expose face data through public dashboards or docs.

## Future Work

- CSV enrollment mapping
- reviewer audit logs
- retention/deletion policy
- clearer operator wording for unknown/low-quality recognition results
- higher-resolution face evidence path before any broader identity pilot
