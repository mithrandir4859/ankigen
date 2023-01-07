---
q: Should we fetch reason for visit before other transformers like parser?

/2023 Jan 05, 14:24 2622/

Yes, such order makes sense. This way all the parsing may still happen in the parsing class like `EpicCdshParser`.

---