<?php
/**
 * Title: Agency landing page
 * Slug: benchmark-fixture/landing
 * Categories: featured, northline
 * Description: Complete Northline landing page: hero, services, selected work, testimonial, FAQ and contact.
 */

$studio    = esc_url( get_theme_file_uri( 'assets/studio.svg' ) );
$fieldwork = esc_url( get_theme_file_uri( 'assets/fieldwork.svg' ) );
$form      = esc_url( get_theme_file_uri( 'assets/form.svg' ) );
?>
<!-- wp:group {"tagName":"section","anchor":"home","className":"northline-section northline-hero","layout":{"type":"constrained"},"style":{"spacing":{"padding":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|60"},"blockGap":"1.5rem"}}} -->
<section class="wp-block-group northline-section northline-hero" id="home" style="padding-top:var(--wp--preset--spacing--60);padding-bottom:var(--wp--preset--spacing--60)">
<!-- wp:paragraph {"className":"northline-kicker"} -->
<p class="northline-kicker">Independent digital studio · Lisbon / Everywhere</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1,"className":"northline-headline"} -->
<h1 class="wp-block-heading northline-headline">Good ideas deserve a great home.</h1>
<!-- /wp:heading -->

<!-- wp:paragraph {"className":"northline-lede","fontSize":"large"} -->
<p class="northline-lede has-large-font-size">We build brands and WordPress experiences for people moving the world forward.</p>
<!-- /wp:paragraph -->

<!-- wp:buttons {"style":{"spacing":{"margin":{"top":"0.5rem"}}}} -->
<div class="wp-block-buttons" style="margin-top:0.5rem">
<!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="#contact">Start a project</a></div>
<!-- /wp:button -->
</div>
<!-- /wp:buttons -->

<!-- wp:image {"sizeSlug":"full","linkDestination":"none","className":"northline-artwork","style":{"spacing":{"margin":{"top":"var:preset|spacing|50"}}}} -->
<figure class="wp-block-image size-full northline-artwork" style="margin-top:var(--wp--preset--spacing--50)"><img src="<?php echo $studio; ?>" alt="Northline studio mark: a dark square set in the centre of a globe drawn in fine lines on a pale moss field." width="1200" height="800"/></figure>
<!-- /wp:image -->
</section>
<!-- /wp:group -->

<!-- wp:group {"tagName":"section","anchor":"services","className":"northline-section","layout":{"type":"constrained"},"style":{"spacing":{"padding":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|60"},"blockGap":"1rem"}}} -->
<section class="wp-block-group northline-section" id="services" style="padding-top:var(--wp--preset--spacing--60);padding-bottom:var(--wp--preset--spacing--60)">
<!-- wp:paragraph {"className":"northline-kicker"} -->
<p class="northline-kicker">01 / What we do</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Small team. Full picture.</h2>
<!-- /wp:heading -->

<!-- wp:columns {"style":{"spacing":{"margin":{"top":"1.5rem"},"blockGap":{"left":"3rem","top":"2rem"}}}} -->
<div class="wp-block-columns" style="margin-top:1.5rem">
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Brand strategy</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Find your voice. Define your direction. Make every touchpoint count.</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">WordPress development</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Fast, flexible websites your team can confidently make their own.</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Care and growth</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Thoughtful improvements, ongoing support, and room to evolve.</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->
</div>
<!-- /wp:columns -->
</section>
<!-- /wp:group -->

<!-- wp:group {"tagName":"section","anchor":"portfolio","className":"northline-section","layout":{"type":"constrained"},"style":{"spacing":{"padding":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|60"},"blockGap":"1rem"}}} -->
<section class="wp-block-group northline-section" id="portfolio" style="padding-top:var(--wp--preset--spacing--60);padding-bottom:var(--wp--preset--spacing--60)">
<!-- wp:paragraph {"className":"northline-kicker"} -->
<p class="northline-kicker">02 / Selected work</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Made for what comes next.</h2>
<!-- /wp:heading -->

<!-- wp:columns {"style":{"spacing":{"margin":{"top":"1.5rem"},"blockGap":{"left":"2.5rem","top":"2.5rem"}}}} -->
<div class="wp-block-columns" style="margin-top:1.5rem">
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:image {"sizeSlug":"full","linkDestination":"none","className":"northline-artwork"} -->
<figure class="wp-block-image size-full northline-artwork"><img src="<?php echo $fieldwork; ?>" alt="Fieldwork project artwork: a navy square inside a line-drawn globe on a pale blue field, captioned a new perspective." width="1200" height="800"/></figure>
<!-- /wp:image -->

<!-- wp:heading {"level":3,"style":{"spacing":{"margin":{"top":"1.25rem"}}}} -->
<h3 class="wp-block-heading" style="margin-top:1.25rem">Fieldwork</h3>
<!-- /wp:heading -->

<!-- wp:paragraph {"fontSize":"small","style":{"spacing":{"margin":{"top":"0.5rem"}}}} -->
<p class="has-small-font-size" style="margin-top:0.5rem">Strategy · Identity · WordPress</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:image {"sizeSlug":"full","linkDestination":"none","className":"northline-artwork"} -->
<figure class="wp-block-image size-full northline-artwork"><img src="<?php echo $form; ?>" alt="Form project artwork: a deep brown square inside a line-drawn globe on a clay-pink field, captioned objects with intention." width="1200" height="800"/></figure>
<!-- /wp:image -->

<!-- wp:heading {"level":3,"style":{"spacing":{"margin":{"top":"1.25rem"}}}} -->
<h3 class="wp-block-heading" style="margin-top:1.25rem">Form</h3>
<!-- /wp:heading -->

<!-- wp:paragraph {"fontSize":"small","style":{"spacing":{"margin":{"top":"0.5rem"}}}} -->
<p class="has-small-font-size" style="margin-top:0.5rem">E-commerce · Digital experience</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->
</div>
<!-- /wp:columns -->
</section>
<!-- /wp:group -->

<!-- wp:group {"tagName":"section","anchor":"testimonials","className":"northline-section","layout":{"type":"constrained"},"style":{"spacing":{"padding":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|60"},"blockGap":"1rem"}}} -->
<section class="wp-block-group northline-section" id="testimonials" style="padding-top:var(--wp--preset--spacing--60);padding-bottom:var(--wp--preset--spacing--60)">
<!-- wp:paragraph {"className":"northline-kicker"} -->
<p class="northline-kicker">03 / Working together</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">A partner, from first idea to launch.</h2>
<!-- /wp:heading -->

<!-- wp:quote {"className":"northline-quote"} -->
<blockquote class="wp-block-quote northline-quote">
<!-- wp:paragraph -->
<p>“Northline made a complicated launch feel clear, collaborative, and genuinely exciting.”</p>
<!-- /wp:paragraph -->
<cite>Alex Morgan, founder of Fieldwork</cite></blockquote>
<!-- /wp:quote -->
</section>
<!-- /wp:group -->

<!-- wp:group {"tagName":"section","anchor":"faq","className":"northline-section","layout":{"type":"constrained"},"style":{"spacing":{"padding":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|60"},"blockGap":"1rem"}}} -->
<section class="wp-block-group northline-section" id="faq" style="padding-top:var(--wp--preset--spacing--60);padding-bottom:var(--wp--preset--spacing--60)">
<!-- wp:paragraph {"className":"northline-kicker"} -->
<p class="northline-kicker">04 / A few answers</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Before we begin.</h2>
<!-- /wp:heading -->

<!-- wp:group {"className":"northline-faq","layout":{"type":"constrained","contentSize":"780px","justifyContent":"left"},"style":{"spacing":{"margin":{"top":"1.5rem"},"blockGap":"0"}}} -->
<div class="wp-block-group northline-faq" style="margin-top:1.5rem">
<!-- wp:details -->
<details class="wp-block-details"><summary>What does a project cost?</summary>
<!-- wp:paragraph -->
<p>Every brief is different. We define scope and a clear proposal together.</p>
<!-- /wp:paragraph -->
</details>
<!-- /wp:details -->

<!-- wp:details -->
<details class="wp-block-details"><summary>How long does a website take?</summary>
<!-- wp:paragraph -->
<p>Most studio websites take six to eight weeks, from discovery to launch.</p>
<!-- /wp:paragraph -->
</details>
<!-- /wp:details -->

<!-- wp:details -->
<details class="wp-block-details"><summary>Can our team edit the website?</summary>
<!-- wp:paragraph -->
<p>Yes. Your content stays editable in WordPress, with a practical handover included.</p>
<!-- /wp:paragraph -->
</details>
<!-- /wp:details -->
</div>
<!-- /wp:group -->
</section>
<!-- /wp:group -->

<!-- wp:group {"tagName":"section","anchor":"contact","className":"northline-section northline-contact","layout":{"type":"constrained"},"style":{"spacing":{"padding":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|60"},"blockGap":"1rem"}}} -->
<section class="wp-block-group northline-section northline-contact" id="contact" style="padding-top:var(--wp--preset--spacing--60);padding-bottom:var(--wp--preset--spacing--60)">
<!-- wp:paragraph {"className":"northline-kicker"} -->
<p class="northline-kicker">05 / Your next chapter</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Let’s make something matter.</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Tell us where you want to go. We’ll help you find the way.</p>
<!-- /wp:paragraph -->

<!-- wp:group {"className":"northline-form","layout":{"type":"constrained","contentSize":"680px","justifyContent":"left"},"style":{"spacing":{"margin":{"top":"1rem"}}}} -->
<div class="wp-block-group northline-form" style="margin-top:1rem">
<!-- wp:shortcode -->
[benchmark_contact]
<!-- /wp:shortcode -->
</div>
<!-- /wp:group -->
</section>
<!-- /wp:group -->
