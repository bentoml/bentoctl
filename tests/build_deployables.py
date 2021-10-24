import asyncio
import os
import bcdt.deployment_store as ds


async def build_deployables(operator, deployment):
    for i in range(3):
        print(f"adding {operator}/{deployment}/{i}")
        os.mkdir("test")
        ds.add(operator, deployment, "test")
        await asyncio.sleep(70)


async def main():
    tasks = []
    for operator in ["aws-lambda", "aws-sagemaker", "gcp-cloud-run"]:
        for deployment in ["iristest", "frauddet", "happyorsad"]:
            tasks.append(build_deployables(operator, deployment))
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
