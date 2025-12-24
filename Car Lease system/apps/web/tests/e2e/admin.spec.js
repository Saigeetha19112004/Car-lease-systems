const { test, expect } = require('@playwright/test')

const API_BASE = process.env.API_BASE || 'http://localhost:8000'
const APP_BASE = process.env.APP_BASE || 'http://localhost:3000'

test('admin create car, upload image, set primary and delete', async ({ page, request }) => {
  // seed admin user via test endpoint
  const seed = await request.post(`${API_BASE}/api/v1/test/seed-admin`, { data: { email: 'e2e-admin@example.com', password: 'password' } })
  expect(seed.ok()).toBeTruthy()
  const seedJson = await seed.json()
  const token = seedJson.access_token

  // set token in localStorage and navigate to admin cars
  await page.addInitScript(token => window.localStorage.setItem('auth-token', token), token)
  await page.goto(`${APP_BASE}/admin/cars`)
  await page.waitForSelector('text=Admin Cars')

  // create a car via UI
  await page.goto(`${APP_BASE}/admin/cars/new`)
  await page.fill('input[placeholder=make]', 'E2EMake')
  await page.fill('input[placeholder=model]', 'E2EModel')
  await page.fill('input[placeholder=year]', '2025')
  await page.fill('input[placeholder=monthly]', '350')
  await page.click('text=Create')

  // back to admin list and check new car exists
  await page.goto(`${APP_BASE}/admin/cars`)
  await expect(page.locator('text=E2EMake')).toBeVisible()

  // open edit page
  const href = await page.locator('a', { hasText: 'Edit' }).first().getAttribute('href')
  await page.goto(APP_BASE + href)
  await page.waitForSelector('text=Edit')

  // upload image
  const filePath = require('path').resolve(__dirname, '../../fixtures/test.png')
  await page.setInputFiles('input[type=file]', filePath)
  await page.click('text=Upload')
  await page.waitForSelector('img')

  // set primary (click first Set primary button)
  await page.click('text=Set primary')
  // verify success by reload and checking image present
  await page.reload()
  await expect(page.locator('img')).toHaveCount(1)

  // delete image
  await page.click('text=Delete')
  // confirm deletion prompt handled in UI
  await page.waitForTimeout(500)
  await page.reload()
  await expect(page.locator('img')).toHaveCount(0)

  // navigate to admin reports and verify counts
  await page.goto(`${APP_BASE}/admin/reports`)
  await page.waitForSelector('text=Admin Reports')
  await expect(page.locator('text=Cars:')).toBeVisible()
  await expect(page.locator('text=Leases:')).toBeVisible()
  await expect(page.locator('text=Payments:')).toBeVisible()
  await expect(page.locator('text=Users:')).toBeVisible()
})

test('end-to-end quote -> accept -> checkout page present', async ({ page, request }) => {
  // create car via API for customer flow
  const carRes = await request.post(`${API_BASE}/api/v1/cars`, { data: { make: 'FlowMake', model: 'FlowModel', year: 2024, base_monthly_price: 199.99 } })
  expect(carRes.ok()).toBeTruthy()
  const car = await carRes.json()

  // visit public cars page and click Get Quote
  await page.goto(`${APP_BASE}/cars`)
  await page.click(`text=${car.make}`)
  await page.goto(`${APP_BASE}/quote/${car.id}`)
  await page.fill('input[placeholder=year]', '2024') // ensure page loaded
  await page.fill('input[placeholder="Term (months):"]', '36').catch(()=>{})

  // click 'Get Quote & Create Lease' button
  await page.click('text=Get Quote & Create Lease')

  // after accept, should redirect to checkout
  await page.waitForURL('**/checkout/**')
  await expect(page.locator('#paypal-buttons')).toBeVisible()
})
