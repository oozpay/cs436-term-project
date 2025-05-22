const { Storage } = require('@google-cloud/storage');
const path = require('path');
const fs = require('fs').promises;

const storage = new Storage();

exports.backupLog = async (event, context) => {
  const bucketName = event.bucket;
  const fileName = event.name;

  console.log(`New file uploaded: ${fileName} in bucket ${bucketName}`);

  // Skip folders
  if (!fileName || fileName.endsWith('/')) return;

  const destPath = path.join('/tmp', path.basename(fileName));

  try {
    await storage.bucket(bucketName).file(fileName).download({ destination: destPath });
    console.log(`Downloaded file to ${destPath}`);

    const content = await fs.readFile(destPath, 'utf8');
    console.log('File content (first 100 chars):', content.slice(0, 100));
  } catch (err) {
    console.error('Error downloading or reading file:', err);
  }
};
