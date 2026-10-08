<?php
/**
 * Title: Agency landing page
 * Slug: benchmark-fixture/landing
 * Categories: featured
 * Description: Complete Northline agency landing page with hero, services, portfolio, testimonial, FAQ and contact sections.
 */

$northline_studio    = esc_url( get_theme_file_uri( 'assets/studio.svg' ) );
$northline_fieldwork = esc_url( get_theme_file_uri( 'assets/fieldwork.svg' ) );
$northline_form      = esc_url( get_theme_file_uri( 'assets/form.svg' ) );
?>
<!-- wp:group {"tagName":"section","anchor":"home","className":"northline-section northline-hero","style":{"spacing":{"padding":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|60"},"blockGap":"1.5rem"}},"layout":{"type":"constrained"}} -->
<section id="home" class="wp-block-group northline-section northline-hero" style="padding-top:var(--wp--preset--spacing--60);padding-bottom:var(--wp--preset--spacing--60)">
<!-- wp:paragraph {"className":"northline-eyebrow","style":{"typography":{"fontSize":"var:preset|font-size|small","textTransform":"uppercase","letterSpacing":"0.14em","fontWeight":"700"},"spacing":{"margin":{"bottom":"1rem"}}}} -->
<p class="northline-eyebrow has-small-font-size" style="margin-bottom:1rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase">Independent digital studio · Lisbon / Everywhere</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1,"style":{"layout":{"selfStretch":"fixed","flexSize":"100%"},"spacing":{"margin":{"top":"0","bottom":"1.5rem"}}}} -->
<h1 class="wp-block-heading" style="margin-top:0;margin-bottom:1.5rem">Good ideas deserve a great home.</h1>
<!-- /wp:heading -->

<!-- wp:paragraph {"className":"northline-lede","style":{"typography":{"fontSize":"1.25rem"}}} -->
<p class="northline-lede" style="font-size:1.25rem">We build brands and WordPress experiences for people moving the world forward.</p>
<!-- /wp:paragraph -->

<!-- wp:buttons {"style":{"spacing":{"margin":{"top":"2rem","bottom":"3rem"}}}} -->
<div class="wp-block-buttons" style="margin-top:2rem;margin-bottom:3rem">
<!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="#contact">Start a project</a></div>
<!-- /wp:button -->
</div>
<!-- /wp:buttons -->

<!-- wp:image {"sizeSlug":"full","linkDestination":"none","align":"wide","className":"northline-artwork"} -->
<figure class="wp-block-image alignwide size-full northline-artwork"><img src="<?php echo $northline_studio; ?>" alt="Line drawing of a globe with a solid dark square at its centre, captioned Northline, independent by design" /></figure>
<!-- /wp:image -->
</section>
<!-- /wp:group -->

<!-- wp:group {"tagName":"section","anchor":"services","className":"northline-section","style":{"spacing":{"padding":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|60"},"blockGap":"1.25rem"},"border":{"top":{"color":"var:preset|color|line","style":"solid","width":"1px"}}},"layout":{"type":"constrained"}} -->
<section id="services" class="wp-block-group northline-section" style="border-top-color:var(--wp--preset--color--line);border-top-style:solid;border-top-width:1px;padding-top:var(--wp--preset--spacing--60);padding-bottom:var(--wp--preset--spacing--60)">
<!-- wp:paragraph {"className":"northline-eyebrow","style":{"typography":{"fontSize":"var:preset|font-size|small","textTransform":"uppercase","letterSpacing":"0.14em","fontWeight":"700"},"spacing":{"margin":{"bottom":"1rem"}}}} -->
<p class="northline-eyebrow has-small-font-size" style="margin-bottom:1rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase">01 / What we do</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2,"style":{"spacing":{"margin":{"top":"0","bottom":"2rem"}}}} -->
<h2 class="wp-block-heading" style="margin-top:0;margin-bottom:2rem">Small team. Full picture.</h2>
<!-- /wp:heading -->

<!-- wp:columns {"style":{"spacing":{"blockGap":{"top":"2rem","left":"3rem"}}}} -->
<div class="wp-block-columns">
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:heading {"level":3,"style":{"spacing":{"margin":{"bottom":"0.75rem"}}}} -->
<h3 class="wp-block-heading" style="margin-bottom:0.75rem">Brand strategy</h3>
<!-- /wp:heading -->

<!-- wp:paragraph {"style":{"typography":{"fontSize":"1rem"}}} -->
<p style="font-size:1rem">Find your voice. Define your direction. Make every touchpoint count.</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:heading {"level":3,"style":{"spacing":{"margin":{"bottom":"0.75rem"}}}} -->
<h3 class="wp-block-heading" style="margin-bottom:0.75rem">WordPress development</h3>
<!-- /wp:heading -->

<!-- wp:paragraph {"style":{"typography":{"fontSize":"1rem"}}} -->
<p style="font-size:1rem">Fast, flexible websites your team can confidently make their own.</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:heading {"level":3,"style":{"spacing":{"margin":{"bottom":"0.75rem"}}}} -->
<h3 class="wp-block-heading" style="margin-bottom:0.75rem">Care and growth</h3>
<!-- /wp:heading -->

<!-- wp:paragraph {"style":{"typography":{"fontSize":"1rem"}}} -->
<p style="font-size:1rem">Thoughtful improvements, ongoing support, and room to evolve.</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->
</div>
<!-- /wp:columns -->
</section>
<!-- /wp:group -->

<!-- wp:group {"tagName":"section","anchor":"portfolio","className":"northline-section","style":{"spacing":{"padding":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|60"},"blockGap":"1.25rem"},"border":{"top":{"color":"var:preset|color|line","style":"solid","width":"1px"}}},"layout":{"type":"constrained"}} -->
<section id="portfolio" class="wp-block-group northline-section" style="border-top-color:var(--wp--preset--color--line);border-top-style:solid;border-top-width:1px;padding-top:var(--wp--preset--spacing--60);padding-bottom:var(--wp--preset--spacing--60)">
<!-- wp:paragraph {"className":"northline-eyebrow","style":{"typography":{"fontSize":"var:preset|font-size|small","textTransform":"uppercase","letterSpacing":"0.14em","fontWeight":"700"},"spacing":{"margin":{"bottom":"1rem"}}}} -->
<p class="northline-eyebrow has-small-font-size" style="margin-bottom:1rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase">02 / Selected work</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2,"style":{"spacing":{"margin":{"top":"0","bottom":"2rem"}}}} -->
<h2 class="wp-block-heading" style="margin-top:0;margin-bottom:2rem">Made for what comes next.</h2>
<!-- /wp:heading -->

<!-- wp:columns {"style":{"spacing":{"blockGap":{"top":"2.5rem","left":"2.5rem"}}}} -->
<div class="wp-block-columns">
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:image {"sizeSlug":"full","linkDestination":"none","className":"northline-artwork"} -->
<figure class="wp-block-image size-full northline-artwork"><img src="<?php echo $northline_fieldwork; ?>" alt="Fieldwork project artwork: a navy globe line drawing with a solid square on a pale blue background, captioned a new perspective" /></figure>
<!-- /wp:image -->

<!-- wp:heading {"level":3,"style":{"spacing":{"margin":{"top":"1.25rem","bottom":"0.5rem"}}}} -->
<h3 class="wp-block-heading" style="margin-top:1.25rem;margin-bottom:0.5rem">Fieldwork</h3>
<!-- /wp:heading -->

<!-- wp:paragraph {"style":{"typography":{"fontSize":"0.9375rem"}}} -->
<p style="font-size:0.9375rem">Strategy · Identity · WordPress</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:image {"sizeSlug":"full","linkDestination":"none","className":"northline-artwork"} -->
<figure class="wp-block-image size-full northline-artwork"><img src="<?php echo $northline_form; ?>" alt="Form project artwork: a brown globe line drawing with a solid square on a terracotta background, captioned objects with intention" /></figure>
<!-- /wp:image -->

<!-- wp:heading {"level":3,"style":{"spacing":{"margin":{"top":"1.25rem","bottom":"0.5rem"}}}} -->
<h3 class="wp-block-heading" style="margin-top:1.25rem;margin-bottom:0.5rem">Form</h3>
<!-- /wp:heading -->

<!-- wp:paragraph {"style":{"typography":{"fontSize":"0.9375rem"}}} -->
<p style="font-size:0.9375rem">E-commerce · Digital experience</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->
</div>
<!-- /wp:columns -->
</section>
<!-- /wp:group -->

<!-- wp:group {"tagName":"section","anchor":"testimonials","className":"northline-section","style":{"spacing":{"padding":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|60"},"blockGap":"1.25rem"},"border":{"top":{"color":"var:preset|color|line","style":"solid","width":"1px"}}},"layout":{"type":"constrained"}} -->
<section id="testimonials" class="wp-block-group northline-section" style="border-top-color:var(--wp--preset--color--line);border-top-style:solid;border-top-width:1px;padding-top:var(--wp--preset--spacing--60);padding-bottom:var(--wp--preset--spacing--60)">
<!-- wp:paragraph {"className":"northline-eyebrow","style":{"typography":{"fontSize":"var:preset|font-size|small","textTransform":"uppercase","letterSpacing":"0.14em","fontWeight":"700"},"spacing":{"margin":{"bottom":"1rem"}}}} -->
<p class="northline-eyebrow has-small-font-size" style="margin-bottom:1rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase">03 / Working together</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2,"style":{"spacing":{"margin":{"top":"0","bottom":"2rem"}}}} -->
<h2 class="wp-block-heading" style="margin-top:0;margin-bottom:2rem">A partner, from first idea to launch.</h2>
<!-- /wp:heading -->

<!-- wp:quote {"className":"northline-quote","style":{"spacing":{"padding":{"left":"0"}},"border":{"width":"0","style":"none"}}} -->
<blockquote class="wp-block-quote northline-quote" style="border-style:none;border-width:0;padding-left:0">
<!-- wp:paragraph {"style":{"typography":{"fontFamily":"var:preset|font-family|editorial","fontSize":"var:preset|font-size|x-large","lineHeight":"1.2"},"layout":{"selfStretch":"fixed","flexSize":"100%"}}} -->
<p class="has-editorial-font-family has-x-large-font-size" style="line-height:1.2">“Northline made a complicated launch feel clear, collaborative, and genuinely exciting.”</p>
<!-- /wp:paragraph -->
<cite>Alex Morgan, founder of Fieldwork</cite></blockquote>
<!-- /wp:quote -->
</section>
<!-- /wp:group -->

<!-- wp:group {"tagName":"section","anchor":"faq","className":"northline-section","style":{"spacing":{"padding":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|60"},"blockGap":"0"},"border":{"top":{"color":"var:preset|color|line","style":"solid","width":"1px"}}},"layout":{"type":"constrained"}} -->
<section id="faq" class="wp-block-group northline-section" style="border-top-color:var(--wp--preset--color--line);border-top-style:solid;border-top-width:1px;padding-top:var(--wp--preset--spacing--60);padding-bottom:var(--wp--preset--spacing--60)">
<!-- wp:paragraph {"className":"northline-eyebrow","style":{"typography":{"fontSize":"var:preset|font-size|small","textTransform":"uppercase","letterSpacing":"0.14em","fontWeight":"700"},"spacing":{"margin":{"bottom":"1rem"}}}} -->
<p class="northline-eyebrow has-small-font-size" style="margin-bottom:1rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase">04 / A few answers</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2,"style":{"spacing":{"margin":{"top":"0","bottom":"2rem"}}}} -->
<h2 class="wp-block-heading" style="margin-top:0;margin-bottom:2rem">Before we begin.</h2>
<!-- /wp:heading -->

<!-- wp:group {"className":"northline-faq","style":{"spacing":{"blockGap":"0"}},"layout":{"type":"constrained","contentSize":"780px","justifyContent":"left"}} -->
<div class="wp-block-group northline-faq">
<!-- wp:details {"style":{"spacing":{"padding":{"top":"1.25rem","bottom":"1.25rem"}},"border":{"top":{"color":"var:preset|color|line","style":"solid","width":"1px"}}}} -->
<details class="wp-block-details" style="border-top-color:var(--wp--preset--color--line);border-top-style:solid;border-top-width:1px;padding-top:1.25rem;padding-bottom:1.25rem"><summary>What does a project cost?</summary>
<!-- wp:paragraph -->
<p>Every brief is different. We define scope and a clear proposal together.</p>
<!-- /wp:paragraph -->
</details>
<!-- /wp:details -->

<!-- wp:details {"style":{"spacing":{"padding":{"top":"1.25rem","bottom":"1.25rem"}},"border":{"top":{"color":"var:preset|color|line","style":"solid","width":"1px"}}}} -->
<details class="wp-block-details" style="border-top-color:var(--wp--preset--color--line);border-top-style:solid;border-top-width:1px;padding-top:1.25rem;padding-bottom:1.25rem"><summary>How long does a website take?</summary>
<!-- wp:paragraph -->
<p>Most studio websites take six to eight weeks, from discovery to launch.</p>
<!-- /wp:paragraph -->
</details>
<!-- /wp:details -->

<!-- wp:details {"style":{"spacing":{"padding":{"top":"1.25rem","bottom":"1.25rem"}},"border":{"top":{"color":"var:preset|color|line","style":"solid","width":"1px"}}}} -->
<details class="wp-block-details" style="border-top-color:var(--wp--preset--color--line);border-top-style:solid;border-top-width:1px;padding-top:1.25rem;padding-bottom:1.25rem"><summary>Can our team edit the website?</summary>
<!-- wp:paragraph -->
<p>Yes. Your content stays editable in WordPress, with a practical handover included.</p>
<!-- /wp:paragraph -->
</details>
<!-- /wp:details -->
</div>
<!-- /wp:group -->
</section>
<!-- /wp:group -->

<!-- wp:group {"tagName":"section","anchor":"contact","className":"northline-section northline-contact","style":{"spacing":{"padding":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|60"},"blockGap":"1.25rem"},"border":{"top":{"color":"var:preset|color|line","style":"solid","width":"1px"}}},"layout":{"type":"constrained"}} -->
<section id="contact" class="wp-block-group northline-section northline-contact" style="border-top-color:var(--wp--preset--color--line);border-top-style:solid;border-top-width:1px;padding-top:var(--wp--preset--spacing--60);padding-bottom:var(--wp--preset--spacing--60)">
<!-- wp:paragraph {"className":"northline-eyebrow","style":{"typography":{"fontSize":"var:preset|font-size|small","textTransform":"uppercase","letterSpacing":"0.14em","fontWeight":"700"},"spacing":{"margin":{"bottom":"1rem"}}}} -->
<p class="northline-eyebrow has-small-font-size" style="margin-bottom:1rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase">05 / Your next chapter</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2,"style":{"spacing":{"margin":{"top":"0","bottom":"1rem"}}}} -->
<h2 class="wp-block-heading" style="margin-top:0;margin-bottom:1rem">Let’s make something matter.</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Tell us where you want to go. We’ll help you find the way.</p>
<!-- /wp:paragraph -->

<!-- wp:group {"className":"northline-form","style":{"spacing":{"margin":{"top":"1.5rem"}}},"layout":{"type":"constrained","contentSize":"680px","justifyContent":"left"}} -->
<div class="wp-block-group northline-form" style="margin-top:1.5rem">
<!-- wp:shortcode -->
[benchmark_contact]
<!-- /wp:shortcode -->
</div>
<!-- /wp:group -->
</section>
<!-- /wp:group -->
