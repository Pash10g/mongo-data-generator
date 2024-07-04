# mongo-data-generator

## Dependencies

```
pip install pymongo openai streamlit
```

Create database: schema_design_db collection:  "api_keys" with the following document:
```
db.api_keys.insertOne({'api_key' : "<SOME_VAL>"})
```

Set the following env variables:
```
MONGODB_ATLAS_URI=<your_atlas_uri>
OPENAI_API_KEY=<your open ai key>
ASSISTANT_ID=<YOUR ASSITANT ID>
```

## Run
```
streamlit run app.py
```
