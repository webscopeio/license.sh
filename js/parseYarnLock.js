const fs = require('fs');
const lockfile = require('@yarnpkg/lockfile');

/*
  parseYarnLock.js PATH_TO_YARN_LOCK

  Parse yarn lock file into json
 */
const main = (argc, argv) => {
  if (argc < 3 || argc > 3) {
    console.error('parseYarnLock.js [PATH_TO_YARN_LOCK]');
    process.exit(1);
  }
  const file = fs.readFileSync(argv[2], 'utf8');
  const json = lockfile.parse(file);
  console.log(JSON.stringify(json));
};

main(process.argv.length, process.argv);
