import json

from aiohttp import web
from sqlalchemy.exc import IntegrityError

from models import Ad, Base, Session, engine

app = web.Application()


async def orm_cntx(app):
    print("Starting...")
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.drop_all)
        await con.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print("Shutting down...")


@web.middleware
async def session_middleware(request, handler):
    async with Session() as session:
        request["session"] = session
        return await handler(request)


app.cleanup_ctx.append(orm_cntx)
app.middlewares.append(session_middleware)


def get_http_error(http_error_class, message):
    return http_error_class(
        text=json.dumps({"error": message}), content_type="application/json"
    )


async def get_ad(ad_id, session):
    ad = await session.get(Ad, ad_id)
    if ad is None:
        raise get_http_error(web.HTTPNotFound, "Ad was not found")
    return ad


class AdsView(web.View):
    def session(self):
        return self.request["session"]

    def ad_id(self):
        return int(self.request.match_info["ad_id"])

    async def get(self):
        ad = await get_ad(self.ad_id(), self.session())
        return web.json_response(
            {
                "id": ad.id,
                "title": ad.title,
                "description": ad.description,
                "created": str(ad.created_at),
                "author": ad.author
            }
        )

    async def post(self):
        json_data = await self.request.json()
        new_ad = Ad(**json_data)
        try:
            self.session().add(new_ad)
            await self.session().commit()
        except IntegrityError:
            raise get_http_error(web.HTTPConflict, "Ad already exists")
        return web.json_response({"id": new_ad.id})

    async def patch(self):
        json_data = await self.request.json()
        ad = await get_ad(self.ad_id(), self.session())
        for key, value in json_data.items():
            setattr(ad, key, value)
        try:
            self.session().add(ad)
            await self.session().commit()
        except IntegrityError:
            raise get_http_error(web.HTTPConflict, "Ad already exists")
        return web.json_response({"id": ad.id})

    async def delete(self):
        ad = await get_ad(self.ad_id(), self.session())
        await self.session().delete(ad)
        await self.session().commit()


app.add_routes(
    [
        web.get("/ads/{ad_id:\\d+}/", AdsView),
        web.patch("/ads/{ad_id:\\d+}/", AdsView),
        web.delete("/ads/{ad_id:\\d+}/", AdsView),
        web.post("/ads/", AdsView),
    ]
)

if __name__ == "__main__":
    web.run_app(app)
