<?php
/* Plugin Name: Benchmark Fixture */
function bench_component(){return <<<'HTML'
<div onclick="document.getElementById('panel').hidden=false">Details</div><div id="panel" hidden>More information</div>
HTML;
}
