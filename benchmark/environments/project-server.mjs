/** JSON-lines bridge: receives only candidate files and public fixture. */
import readline from 'node:readline';
import {ProjectRuntime} from './project-runtime.mjs';
const runtime=new ProjectRuntime();
try {
  for await(const line of readline.createInterface({input:process.stdin})) {
    let result;
    try {
      const req=JSON.parse(line);
      if(req.op==='start'){await runtime.start(req.blueprint);result={ready:true};}
      else if(req.op==='sync'){await runtime.sync(req.files,req.fixture);result={ready:true};}
      else if(req.op==='preview')result=await runtime.snapshot();
      else if(req.op==='public_checks')result=await runtime.publicChecks();
      else if(req.op==='browser')result=await runtime.action(req.arguments);
      else throw Error('Unknown operation');
    } catch(error){result={error:String(error.message).slice(0,2000)};}
    process.stdout.write('@@BENCH@@'+JSON.stringify(result)+'\n');
  }
} finally {await runtime.close();}
