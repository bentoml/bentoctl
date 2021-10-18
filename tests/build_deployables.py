import asyncio
import bcdt.deployment_store as ds


async def build_deployables(plugin, deployment):
    for i in range(3):
        print(f"adding {plugin}/{deployment}/{i}")
        ds.add(plugin, deployment, "../sklearn")
        await asyncio.sleep(70)


async def main():
    tasks = []
    for plugin in ["aws-lambda", "aws-sagemaker", "gcp-cloud-run"]:
        for deployment in ["iristest", "frauddet", "happyorsad"]:
            tasks.append(build_deployables(plugin, deployment))
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
