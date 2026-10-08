<?php
/* Plugin Name: Benchmark Fixture */
function bench_component(){
return <<<'HTML'
<form role="search" method="get" class="bench-search-form" action="" style="display:flex;flex-wrap:wrap;align-items:flex-end;gap:8px;max-width:100%;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
<style>
.bench-search-form{display:flex;flex-wrap:wrap;align-items:flex-end;gap:8px;max-width:100%;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;}
.bench-search-label{display:block;width:100%;font-size:14px;font-weight:600;color:#0e2a47;line-height:1.4;margin:0 0 2px 0;}
.bench-search-input{flex:1 1 200px;min-width:0;padding:10px 14px;font-size:16px;line-height:1.5;color:#0e2a47;background-color:#ffffff;border:2px solid #334e68;border-radius:4px;box-sizing:border-box;}
.bench-search-input::placeholder{color:#486581;opacity:1;}
.bench-search-input:focus,.bench-search-input:focus-visible{outline:3px solid #0d3ea8;outline-offset:2px;border-color:#0d3ea8;}
.bench-search-submit{padding:10px 20px;font-size:15px;font-weight:600;line-height:1.5;color:#ffffff;background-color:#0d3ea8;border:2px solid #0d3ea8;border-radius:4px;cursor:pointer;box-sizing:border-box;white-space:nowrap;}
.bench-search-submit:hover{background-color:#092b77;border-color:#092b77;}
.bench-search-submit:focus,.bench-search-submit:focus-visible{outline:3px solid #0d3ea8;outline-offset:2px;background-color:#092b77;border-color:#092b77;}
@media (prefers-reduced-motion: reduce){.bench-search-submit{transition:none;}}
</style>
<label for="bench-search-s" class="bench-search-label" style="display:block;width:100%;font-size:14px;font-weight:600;color:#0e2a47;line-height:1.4;margin:0 0 2px 0;">Search</label>
<input type="search" id="bench-search-s" name="s" class="bench-search-input" aria-label="Search" placeholder="Search" value="" style="flex:1 1 200px;min-width:0;padding:10px 14px;font-size:16px;line-height:1.5;color:#0e2a47;background-color:#ffffff;border:2px solid #334e68;border-radius:4px;box-sizing:border-box;" />
<button type="submit" id="bench-search-submit" name="Search" value="Search" class="bench-search-submit" style="padding:10px 20px;font-size:15px;font-weight:600;line-height:1.5;color:#ffffff;background-color:#0d3ea8;border:2px solid #0d3ea8;border-radius:4px;cursor:pointer;box-sizing:border-box;white-space:nowrap;">Search</button>
</form>
HTML;
}
