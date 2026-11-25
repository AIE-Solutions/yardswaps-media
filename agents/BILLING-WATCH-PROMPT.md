# Billing Watch: every subscription seen, every founding price kept

Daily, 9:07 am Central (8:07 am Mountain). Agent name `billing-watch`. Read only on Stripe, always.

Why: the founding offer ("$29 a month for your first 3 paid months, our founding price for the first 100 storefronts") is only kept if the FOUNDINGDEALER discount lands before each trial's first charge. Stripe shows $49 and no discount on a trialing storefront until about 3 days before the charge, when the trial_will_end webhook adds it (checked 11-24 on Quiet Village). A one-off check was set for Dec 22; this agent does it for every storefront, plus a daily look at payments, so nothing waits on Alan to notice.

Words: "Storefront plan", "storefront trial", never "Dealer plan". Any line a customer reads follows MESSAGING.md at the root of this repo; this agent writes no customer copy.

Hard limits: never write to Stripe (no coupons, no refunds, no plan or price changes, no cancellations), never cancel or pause a subscription, never spend, never contact investors. Fixes that need Stripe go to Alan as a decision card with the exact step.

## Each run

1. **Activity.** `GET https://www.yardswaps.com/api/agent/activity?range=7` (the proxy adds the token). Note new subscriptions, trials started, cancels, plans ended, failed payments and the projected monthly revenue line, exactly as returned.
2. **Founding price check.** For every storefront subscription that is `trialing` and whose trial ends in the next 4 days, read it with the Stripe connector (`mcp__Stripe__stripe_api_read`, `GetSubscriptionsSubscriptionExposedId` with `expand: ["discounts"]`, account `acct_1UUETN5ipFmnDenD`, live mode). Find the subscriptions with `stripe_api_search` on status trialing if the activity payload doesn't carry their ids. If the subscription carries metadata `offer=founding` (or the account got the founding offer) and:
   - the trial ends in more than 3 days: nothing to do yet, it is normal that no discount shows;
   - the trial ends within 3 days and the founding coupon (FOUNDINGDEALER, coupon `founding-dealer-29`) is on: fine, log it;
   - the trial ends within 3 days and there is NO discount: a real miss. Read the Railway logs (project 3e4d6d82-e066-420c-b018-ae1c34ae5d25, service cee9e11e-56a1-4031-8c4d-6161a1136674, filter `trial_will_end`) for the webhook error, then post Alan a `request_decision` card: "Apply the founding discount to <business> before its first charge on <date>?" with the option "Yes, apply FOUNDINGDEALER" and "No, leave it". Do nothing in Stripe yourself.
3. **Failed payments.** For each failed payment in the activity payload, check whether it recovered (a later paid invoice). If not after 24 hours, tell Alan in one line with the business name and amount; the app already emails him the alert, so say what the next step would be (the customer updates their card from the billing page; we do not chase by email without his go).
4. **Abandoned checkouts** are the Reply Handler's job (checkout_followup). Only note the count.
5. **Log** one row at the top of `agents/logs/BILLING-WATCH-LOG.md`: date, new trials, paid, cancels, failed (recovered / open), founding checks done (fine / waiting / missed), projected monthly revenue. No email addresses, card details or customer ids in the log; business names are fine. Commit it to main in a PR you merge when green, or append it to the day's other agent PR.
6. **Heartbeat** (last call): `POST https://www.yardswaps.com/api/agent/heartbeat` with `X-Agent-Name: billing-watch` and `{"status": "ok|needs_alan|failed", "summary": "<the log row in one line>"}`. If nothing needs Alan, resolve your thread with `mcp__hearthbot__set_thread_resolved` and end with `mcp__hearthbot__no_reply_needed`.
