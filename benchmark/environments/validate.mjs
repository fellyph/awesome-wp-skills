import fs from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { validateBlueprint } from '@wp-playground/blueprints';
const root = fileURLToPath(new URL('../tasks/', import.meta.url));
for (const task of await fs.readdir(root)) {
  const blueprint = JSON.parse(await fs.readFile(`${root}/${task}/blueprint.json`, 'utf8'));
  const result = validateBlueprint(blueprint);
  if (!result.valid) throw Error(`${task}: ${JSON.stringify(result.errors)}`);
  if (blueprint.preferredVersions.wp !== '6.9' || blueprint.preferredVersions.php !== '8.3') throw Error(`${task}: unexpected runtime version`);
}
console.log('All task Blueprints match the pinned Playground schema.');
