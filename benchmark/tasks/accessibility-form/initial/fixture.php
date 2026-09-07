<?php
/* Plugin Name: Benchmark Fixture */
function bench_component(){return <<<'HTML'
<form><input type="search" name="s"><div onclick="this.parentNode.submit()">Search</div></form>
HTML;
}
