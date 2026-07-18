_Users Schema_
{
$jsonSchema: {
bsonType: 'object',
required: [
'name',
'phone_number'
],
properties: {
name: {
bsonType: 'string',
description: 'required'
},
phone_number: {
bsonType: 'string',
description: 'required'
},
teammate_name: {
bsonType: 'string'
},
topic_id: {
bsonType: 'objectId',
description: 'reference to topics collection'
},
custom_topic: {
bsonType: 'string',
description: 'optional custom topic (mutually exclusive with topic_id)'
}
}
}
}

---

_Topic Schema_

{
$jsonSchema: {
bsonType: 'object',
required: [
'id',
'topic_name',
'count',
'complete'
],
properties: {
id: {
bsonType: 'int',
description: 'required'
},
topic_name: {
bsonType: 'string',
description: 'required'
},
count: {
bsonType: 'int',
minimum: 0,
maximum: 3,
description: 'required, 0 to 3'
},
complete: {
bsonType: 'bool',
description: 'required'
}
}
}
}
