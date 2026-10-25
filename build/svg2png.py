import asyncio,sys
from playwright.async_api import async_playwright
async def main(src,out,size):
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':size,'height':size},device_scale_factor=1)
        await pg.set_content(f'<style>html,body{{margin:0;background:transparent}}</style><img src="file://{src}" style="width:{size}px;height:{size}px;display:block">')
        await pg.wait_for_timeout(300); await pg.screenshot(path=out,omit_background=True); await b.close()
asyncio.run(main(sys.argv[1],sys.argv[2],int(sys.argv[3])))
