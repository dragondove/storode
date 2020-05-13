# Cross-referencing code and requirement
---

Example for generating identifier for requirements from user stories:

```bash
# Try to delete ./sample/srs_with_id.txt and then run this command
python ./src/storode.py ./sample/srs.txt
```

Example for generating web pages:

```bash
# Try to delete ./doc and run this command
python ./src/storode.py ./sample/srs_with_id.txt ./sample/src
```

Example for testing collision rate of cut of MD5 digest:

```bash
python ./src/collision.py
```
