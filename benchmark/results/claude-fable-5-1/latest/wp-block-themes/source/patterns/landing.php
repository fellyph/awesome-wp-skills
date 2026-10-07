<?php
/**
 * Title: Agency landing page
 * Slug: benchmark-fixture/landing
 * Categories: northline, featured
 * Description: The complete Northline agency landing page: hero, services, selected work, testimonial, FAQ and contact.
 * Keywords: landing, agency, hero, services, portfolio, contact
 * Viewport Width: 1400
 *
 * @package benchmark-fixture
 */

$northline_studio    = esc_url( get_theme_file_uri( 'assets/studio.svg' ) );
$northline_fieldwork = esc_url( get_theme_file_uri( 'assets/fieldwork.svg' ) );
$northline_form      = esc_url( get_theme_file_uri( 'assets/form.svg' ) );
?>
<!-- wp:group {"tagName":"section","anchor":"home","className":"northline-hero","align":"wide","layout":{"type":"constrained","justifyContent":"left"}} -->
<section class="wp-block-group alignwide northline-hero" id="home"><!-- wp:paragraph {"className":"northline-eyebrow"} -->
<p class="northline-eyebrow">Independent digital studio · Lisbon / Everywhere</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1,"style":{"layout":{"selfStretch":"fixed","flexSize":"100%"}}} -->
<h1 class="wp-block-heading">Good ideas deserve a great home.</h1>
<!-- /wp:heading -->

<!-- wp:paragraph {"className":"northline-lede"} -->
<p class="northline-lede">We build brands and WordPress experiences for people moving the world forward.</p>
<!-- /wp:paragraph -->

<!-- wp:buttons {"style":{"spacing":{"margin":{"top":"1.5rem"}}}} -->
<div class="wp-block-buttons" style="margin-top:1.5rem"><!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="#contact">Start a project</a></div>
<!-- /wp:button --></div>
<!-- /wp:buttons -->

<!-- wp:image {"align":"wide","sizeSlug":"full","linkDestination":"none"} -->
<figure class="wp-block-image alignwide size-full"><img src="<?php echo $northline_studio; ?>" alt="Northline studio artwork: a dark square set inside a globe of intersecting lines on a moss-green field, captioned Northline, independent by design" width="1200" height="800"/></figure>
<!-- /wp:image --></section>
<!-- /wp:group -->

<!-- wp:group {"tagName":"section","anchor":"services","className":"northline-section","align":"wide","layout":{"type":"constrained","justifyContent":"left"}} -->
<section class="wp-block-group alignwide northline-section" id="services"><!-- wp:paragraph {"className":"northline-eyebrow"} -->
<p class="northline-eyebrow">01 / What we do</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">Small team. Full picture.</h2>
<!-- /wp:heading -->

<!-- wp:columns {"align":"wide","className":"northline-columns","style":{"spacing":{"blockGap":{"left":"3rem"},"margin":{"top":"2rem"}}}} -->
<div class="wp-block-columns alignwide northline-columns" style="margin-top:2rem"><!-- wp:column -->
<div class="wp-block-column"><!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Brand strategy</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Find your voice. Define your direction. Make every touchpoint count.</p>
<!-- /wp:paragraph --></div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column"><!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">WordPress development</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Fast, flexible websites your team can confidently make their own.</p>
<!-- /wp:paragraph --></div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column"><!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Care and growth</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Thoughtful improvements, ongoing support, and room to evolve.</p>
<!-- /wp:paragraph --></div>
<!-- /wp:column --></div>
<!-- /wp:columns --></section>
<!-- /wp:group -->

<!-- wp:group {"tagName":"section","anchor":"portfolio","className":"northline-section","align":"wide","layout":{"type":"constrained","justifyContent":"left"}} -->
<section class="wp-block-group alignwide northline-section" id="portfolio"><!-- wp:paragraph {"className":"northline-eyebrow"} -->
<p class="northline-eyebrow">02 / Selected work</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">Made for what comes next.</h2>
<!-- /wp:heading -->

<!-- wp:columns {"align":"wide","className":"northline-columns","style":{"spacing":{"blockGap":{"left":"3rem"},"margin":{"top":"2rem"}}}} -->
<div class="wp-block-columns alignwide northline-columns" style="margin-top:2rem"><!-- wp:column -->
<div class="wp-block-column"><!-- wp:image {"sizeSlug":"full","linkDestination":"none"} -->
<figure class="wp-block-image size-full"><img src="<?php echo $northline_fieldwork; ?>" alt="Fieldwork project artwork: a navy square inside a globe of lines on a pale blue field, captioned Fieldwork, a new perspective" width="1200" height="800"/></figure>
<!-- /wp:image -->

<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Fieldwork</h3>
<!-- /wp:heading -->

<!-- wp:paragraph {"className":"northline-meta"} -->
<p class="northline-meta">Strategy · Identity · WordPress</p>
<!-- /wp:paragraph --></div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column"><!-- wp:image {"sizeSlug":"full","linkDestination":"none"} -->
<figure class="wp-block-image size-full"><img src="<?php echo $northline_form; ?>" alt="Form project artwork: a brown square inside a globe of lines on a terracotta field, captioned Form, objects with intention" width="1200" height="800"/></figure>
<!-- /wp:image -->

<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Form</h3>
<!-- /wp:heading -->

<!-- wp:paragraph {"className":"northline-meta"} -->
<p class="northline-meta">E-commerce · Digital experience</p>
<!-- /wp:paragraph --></div>
<!-- /wp:column --></div>
<!-- /wp:columns --></section>
<!-- /wp:group -->

<!-- wp:group {"tagName":"section","anchor":"testimonials","className":"northline-section","align":"wide","layout":{"type":"constrained","justifyContent":"left"}} -->
<section class="wp-block-group alignwide northline-section" id="testimonials"><!-- wp:paragraph {"className":"northline-eyebrow"} -->
<p class="northline-eyebrow">03 / Working together</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">A partner, from first idea to launch.</h2>
<!-- /wp:heading -->

<!-- wp:quote -->
<blockquote class="wp-block-quote"><!-- wp:paragraph -->
<p>“Northline made a complicated launch feel clear, collaborative, and genuinely exciting.”</p>
<!-- /wp:paragraph --><cite>Alex Morgan, founder of Fieldwork</cite></blockquote>
<!-- /wp:quote --></section>
<!-- /wp:group -->

<!-- wp:group {"tagName":"section","anchor":"faq","className":"northline-section","align":"wide","layout":{"type":"constrained","justifyContent":"left"}} -->
<section class="wp-block-group alignwide northline-section" id="faq"><!-- wp:paragraph {"className":"northline-eyebrow"} -->
<p class="northline-eyebrow">04 / A few answers</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">Before we begin.</h2>
<!-- /wp:heading -->

<!-- wp:group {"className":"northline-faq","style":{"spacing":{"blockGap":"0","margin":{"top":"2rem"}}},"layout":{"type":"default"}} -->
<div class="wp-block-group northline-faq" style="margin-top:2rem"><!-- wp:details -->
<details class="wp-block-details"><summary>What does a project cost?</summary><!-- wp:paragraph -->
<p>Every brief is different. We define scope and a clear proposal together.</p>
<!-- /wp:paragraph --></details>
<!-- /wp:details -->

<!-- wp:details -->
<details class="wp-block-details"><summary>How long does a website take?</summary><!-- wp:paragraph -->
<p>Most studio websites take six to eight weeks, from discovery to launch.</p>
<!-- /wp:paragraph --></details>
<!-- /wp:details -->

<!-- wp:details -->
<details class="wp-block-details"><summary>Can our team edit the website?</summary><!-- wp:paragraph -->
<p>Yes. Your content stays editable in WordPress, with a practical handover included.</p>
<!-- /wp:paragraph --></details>
<!-- /wp:details --></div>
<!-- /wp:group --></section>
<!-- /wp:group -->

<!-- wp:group {"tagName":"section","anchor":"contact","className":"northline-section","align":"wide","layout":{"type":"constrained","justifyContent":"left"}} -->
<section class="wp-block-group alignwide northline-section" id="contact"><!-- wp:paragraph {"className":"northline-eyebrow"} -->
<p class="northline-eyebrow">05 / Your next chapter</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">Let’s make something matter.</h2>
<!-- /wp:heading -->

<!-- wp:paragraph {"className":"northline-lede"} -->
<p class="northline-lede">Tell us where you want to go. We’ll help you find the way.</p>
<!-- /wp:paragraph -->

<!-- wp:group {"className":"northline-contact-form","style":{"spacing":{"margin":{"top":"1.5rem"}}},"layout":{"type":"default"}} -->
<div class="wp-block-group northline-contact-form" style="margin-top:1.5rem"><!-- wp:shortcode -->
[benchmark_contact]
<!-- /wp:shortcode --></div>
<!-- /wp:group --></section>
<!-- /wp:group -->
