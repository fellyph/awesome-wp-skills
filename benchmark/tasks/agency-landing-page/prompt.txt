# Northline / agency landing page / brief v1.0.0

Build an installable WordPress 6.9 block theme for an independent digital agency.
Match the supplied desktop and mobile reference images. Palette: paper #f4f2eb,
ink #213a31, moss #dce6db. Use local Georgia headings and Trebuchet MS body text.
Use the supplied SVG artwork; no external fonts, images, page builders or network.
Preserve meaningful accessible image alternatives and a restrained editorial layout.

Create templates/index.html and templates/front-page.html with native post-content,
reusable parts/header.html and parts/footer.html, and theme.json global styles.
Put the complete editable page in patterns/landing.php, slug benchmark-fixture/landing.
The harness inserts that pattern into a published home page at installation. Do not
replace the editor or hardcode the frontend separately from the editable content.
Use native heading, paragraph, image, button, group, navigation, quote and details blocks.
The fixed [benchmark_contact] shortcode is available. Style it in your theme; do not
reimplement its storage or modify the fixture. It validates name, email and message,
and stores only local synthetic submissions. Never add external submission endpoints.

Header: NORTHLINE /; navigation Services #services, Work #portfolio,
Studio #testimonials, Contact #contact. Mobile navigation must work with a keyboard.
Hero #home: INDEPENDENT DIGITAL STUDIO · LISBON / EVERYWHERE
Heading: Good ideas deserve a great home.
Copy: We build brands and WordPress experiences for people moving the world forward.
Primary button: Start a project → #contact. Artwork: assets/studio.svg.
Services #services: 01 / WHAT WE DO; Small team. Full picture.
Brand strategy — Find your voice. Define your direction. Make every touchpoint count.
WordPress development — Fast, flexible websites your team can confidently make their own.
Care and growth — Thoughtful improvements, ongoing support, and room to evolve.
Portfolio #portfolio: 02 / SELECTED WORK; Made for what comes next.
Fieldwork: assets/fieldwork.svg, Strategy · Identity · WordPress.
Form: assets/form.svg, E-commerce · Digital experience.
Testimonials #testimonials: 03 / WORKING TOGETHER; A partner, from first idea to launch.
“Northline made a complicated launch feel clear, collaborative, and genuinely exciting.”
Attribution: Alex Morgan, founder of Fieldwork.
FAQ #faq: 04 / A FEW ANSWERS; Before we begin.
What does a project cost? Every brief is different. We define scope and a clear proposal together.
How long does a website take? Most studio websites take six to eight weeks, from discovery to launch.
Can our team edit the website? Yes. Your content stays editable in WordPress, with a practical handover included.
Contact #contact: 05 / YOUR NEXT CHAPTER; Let’s make something matter.
Tell us where you want to go. We’ll help you find the way. Include [benchmark_contact].
Footer: NORTHLINE /; Independent minds. Lasting impact.
© 2026 Northline Studio. Built with intention.

Handover: the headline, image and CTA must be editable through the WordPress editor;
saved changes must survive reload and appear on the frontend. Retain assets/replacement.svg
as an available alternative artwork. Layouts are evaluated at desktop and mobile widths.
Resource budgets: total theme at most 1 MB; at most 45 same-origin page requests.
Public checks cover activation, PHP errors, native block validity and basic axe results.
Final tests are hidden. Use preview, browser and public_checks to iterate, then submit.
Automated rubric: WordPress 30, functionality 25, accessibility 20, responsive 15,
technical 10. Critical failures block an artifact pass. Visual review is separate and human.
