const fs = require('fs');
const lockfile = require('@yarnpkg/lockfile');

const main = (argc, argv) => {
  if (argc < 3 || argc > 3) {
    console.error('lockToJson [FILE]');
    process.exit(1);
  }
  const file = fs.readFileSync(argv[2], 'utf8');
  const json = lockfile.parse(file);
  console.log(JSON.stringify(json));
};

main(process.argv.length, process.argv);
