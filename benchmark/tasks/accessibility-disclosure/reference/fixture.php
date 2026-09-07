<?php
/* Plugin Name: Benchmark Fixture */
function bench_component(){return <<<'HTML'
<button type="button" aria-expanded="false" aria-controls="panel" onclick="const p=document.getElementById(this.getAttribute('aria-controls'));p.hidden=!p.hidden;this.setAttribute('aria-expanded',String(!p.hidden))">Details</button><div id="panel" hidden>More information</div>
HTML;
}
