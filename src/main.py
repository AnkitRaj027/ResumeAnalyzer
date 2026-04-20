from ranker import rank_resumes

with open("../data/job.txt", "r") as f:
    job_desc = f.read()


with open("../data/resume.txt", "r") as f:
    resumes = f.read().split("\n")


results = rank_resumes(job_desc, resumes)

print("\n=== Resume Ranking ===\n")
for i, score in results:
    print(f"Resume {i+1} → Score: {score:.4f}")