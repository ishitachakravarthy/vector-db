db = db.getSiblingDB('vector-db');

// Create user
db.createUser({
  user: 'mongodb_user',
  pwd: 'mongodb_password',
  roles: [
    {
      role: 'readWrite',
      db: 'vector-db'
    }
  ]
});

// Import sample data
const libraries = JSON.parse(cat('/sample_libraries.json'));
const documents = JSON.parse(cat('/sample_documents.json'));

db.libraries.insertMany(libraries);
db.documents.insertMany(documents); 