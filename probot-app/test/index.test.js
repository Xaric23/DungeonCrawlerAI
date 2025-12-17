const { Probot, ProbotOctokit } = require("probot");
const nock = require("nock");
const myProbotApp = require("../src/index");

const issueOpenedPayload = require("./fixtures/issues.opened.json");
const pullRequestOpenedPayload = require("./fixtures/pull_request.opened.json");
const issueCommentCreatedPayload = require("./fixtures/issue_comment.created.json");
const releasePublishedPayload = require("./fixtures/release.published.json");

describe("DungeonCrawler Bot", () => {
  let probot;

  beforeEach(() => {
    nock.disableNetConnect();
    probot = new Probot({
      appId: 123,
      privateKey: "test",
      Octokit: ProbotOctokit.defaults({
        retry: { enabled: false },
        throttle: { enabled: false },
      }),
    });
    probot.load(myProbotApp);
  });

  afterEach(() => {
    nock.cleanAll();
    nock.enableNetConnect();
  });

  describe("Issue labeling", () => {
    test("labels a bug issue correctly", async () => {
      const mock = nock("https://api.github.com")
        .post("/app/installations/1/access_tokens")
        .reply(200, { token: "test" })
        .get("/repos/Xaric23/DungeonCrawlerAI/issues?creator=testuser&state=all")
        .reply(200, [issueOpenedPayload.issue])
        .post("/repos/Xaric23/DungeonCrawlerAI/issues/1/labels", (body) => {
          expect(body.labels).toContain("bug");
          return true;
        })
        .reply(200, []);

      await probot.receive({ name: "issues.opened", payload: issueOpenedPayload });
      expect(mock.pendingMocks()).toStrictEqual([]);
    });

    test("labels an enhancement issue correctly", async () => {
      const enhancementPayload = {
        ...issueOpenedPayload,
        issue: {
          ...issueOpenedPayload.issue,
          title: "Add new feature request",
          body: "This would be nice to have",
        },
      };

      const mock = nock("https://api.github.com")
        .post("/app/installations/1/access_tokens")
        .reply(200, { token: "test" })
        .get("/repos/Xaric23/DungeonCrawlerAI/issues?creator=testuser&state=all")
        .reply(200, [enhancementPayload.issue])
        .post("/repos/Xaric23/DungeonCrawlerAI/issues/1/labels", (body) => {
          expect(body.labels).toContain("enhancement");
          return true;
        })
        .reply(200, []);

      await probot.receive({ name: "issues.opened", payload: enhancementPayload });
      expect(mock.pendingMocks()).toStrictEqual([]);
    });

    test("labels a documentation issue correctly", async () => {
      const docPayload = {
        ...issueOpenedPayload,
        issue: {
          ...issueOpenedPayload.issue,
          title: "Update doc",
          body: "Documentation needs update",
        },
      };

      const mock = nock("https://api.github.com")
        .post("/app/installations/1/access_tokens")
        .reply(200, { token: "test" })
        .get("/repos/Xaric23/DungeonCrawlerAI/issues?creator=testuser&state=all")
        .reply(200, [docPayload.issue])
        .post("/repos/Xaric23/DungeonCrawlerAI/issues/1/labels", (body) => {
          expect(body.labels).toContain("documentation");
          return true;
        })
        .reply(200, []);

      await probot.receive({ name: "issues.opened", payload: docPayload });
      expect(mock.pendingMocks()).toStrictEqual([]);
    });
  });

  describe("Welcome messages", () => {
    test("welcomes first-time issue contributor", async () => {
      const mock = nock("https://api.github.com")
        .post("/app/installations/1/access_tokens")
        .reply(200, { token: "test" })
        .get("/repos/Xaric23/DungeonCrawlerAI/issues?creator=testuser&state=all")
        .reply(200, [issueOpenedPayload.issue])
        .post("/repos/Xaric23/DungeonCrawlerAI/issues/1/labels")
        .reply(200, [])
        .post("/repos/Xaric23/DungeonCrawlerAI/issues/1/comments", (body) => {
          expect(body.body).toContain("Welcome to DungeonCrawlerAI");
          expect(body.body).toContain("@testuser");
          return true;
        })
        .reply(200, {});

      await probot.receive({ name: "issues.opened", payload: issueOpenedPayload });
      expect(mock.pendingMocks()).toStrictEqual([]);
    });

    test("does not welcome returning issue contributor", async () => {
      const mock = nock("https://api.github.com")
        .post("/app/installations/1/access_tokens")
        .reply(200, { token: "test" })
        .get("/repos/Xaric23/DungeonCrawlerAI/issues?creator=testuser&state=all")
        .reply(200, [issueOpenedPayload.issue, { ...issueOpenedPayload.issue, number: 2 }])
        .post("/repos/Xaric23/DungeonCrawlerAI/issues/1/labels")
        .reply(200, []);

      await probot.receive({ name: "issues.opened", payload: issueOpenedPayload });
      expect(mock.pendingMocks()).toStrictEqual([]);
    });

    test("welcomes first-time PR contributor", async () => {
      const mock = nock("https://api.github.com")
        .post("/app/installations/1/access_tokens")
        .reply(200, { token: "test" })
        .get("/repos/Xaric23/DungeonCrawlerAI/issues?creator=testuser&state=all")
        .reply(200, [
          {
            number: 1,
            title: pullRequestOpenedPayload.pull_request.title,
            user: pullRequestOpenedPayload.pull_request.user,
            pull_request: {
              url: "https://api.github.com/repos/Xaric23/DungeonCrawlerAI/pulls/1",
            },
          },
        ])
        .post("/repos/Xaric23/DungeonCrawlerAI/issues/1/labels")
        .reply(200, [])
        .post("/repos/Xaric23/DungeonCrawlerAI/issues/1/comments", (body) => {
          expect(body.body).toContain("Thanks for your first PR");
          expect(body.body).toContain("@testuser");
          return true;
        })
        .reply(200, {});

      await probot.receive({
        name: "pull_request.opened",
        payload: pullRequestOpenedPayload,
      });
      expect(mock.pendingMocks()).toStrictEqual([]);
    });
  });

  describe("PR labeling", () => {
    test("labels a bug fix PR correctly", async () => {
      const bugFixPayload = {
        ...pullRequestOpenedPayload,
        pull_request: {
          ...pullRequestOpenedPayload.pull_request,
          title: "Fix bug in game core",
        },
      };

      const mock = nock("https://api.github.com")
        .post("/app/installations/1/access_tokens")
        .reply(200, { token: "test" })
        .post("/repos/Xaric23/DungeonCrawlerAI/issues/1/labels", (body) => {
          expect(body.labels).toContain("bug");
          return true;
        })
        .reply(200, [])
        .get("/repos/Xaric23/DungeonCrawlerAI/issues?creator=testuser&state=all")
        .reply(200, [
          {
            number: 1,
            title: bugFixPayload.pull_request.title,
            user: bugFixPayload.pull_request.user,
            pull_request: {
              url: "https://api.github.com/repos/Xaric23/DungeonCrawlerAI/pulls/1",
            },
          },
        ]);

      await probot.receive({ name: "pull_request.opened", payload: bugFixPayload });
      expect(mock.pendingMocks()).toStrictEqual([]);
    });

    test("labels an enhancement PR correctly", async () => {
      const enhancementPayload = {
        ...pullRequestOpenedPayload,
        pull_request: {
          ...pullRequestOpenedPayload.pull_request,
          title: "Add new feature",
        },
      };

      const mock = nock("https://api.github.com")
        .post("/app/installations/1/access_tokens")
        .reply(200, { token: "test" })
        .post("/repos/Xaric23/DungeonCrawlerAI/issues/1/labels", (body) => {
          expect(body.labels).toContain("enhancement");
          return true;
        })
        .reply(200, [])
        .get("/repos/Xaric23/DungeonCrawlerAI/issues?creator=testuser&state=all")
        .reply(200, [
          {
            number: 1,
            title: enhancementPayload.pull_request.title,
            user: enhancementPayload.pull_request.user,
            pull_request: {
              url: "https://api.github.com/repos/Xaric23/DungeonCrawlerAI/pulls/1",
            },
          },
        ]);

      await probot.receive({ name: "pull_request.opened", payload: enhancementPayload });
      expect(mock.pendingMocks()).toStrictEqual([]);
    });
  });

  describe("Comment reactions", () => {
    test("reacts with heart to thank you comment", async () => {
      const mock = nock("https://api.github.com")
        .post("/app/installations/1/access_tokens")
        .reply(200, { token: "test" })
        .post("/repos/Xaric23/DungeonCrawlerAI/issues/comments/1/reactions", (body) => {
          expect(body.content).toBe("heart");
          return true;
        })
        .reply(200, {});

      await probot.receive({
        name: "issue_comment.created",
        payload: issueCommentCreatedPayload,
      });
      expect(mock.pendingMocks()).toStrictEqual([]);
    });

    test("reacts with hooray to fixed comment", async () => {
      const fixedPayload = {
        ...issueCommentCreatedPayload,
        comment: {
          ...issueCommentCreatedPayload.comment,
          body: "This is now fixed!",
        },
      };

      const mock = nock("https://api.github.com")
        .post("/app/installations/1/access_tokens")
        .reply(200, { token: "test" })
        .post("/repos/Xaric23/DungeonCrawlerAI/issues/comments/1/reactions", (body) => {
          expect(body.content).toBe("hooray");
          return true;
        })
        .reply(200, {});

      await probot.receive({
        name: "issue_comment.created",
        payload: fixedPayload,
      });
      expect(mock.pendingMocks()).toStrictEqual([]);
    });
  });

  describe("Release notes", () => {
    test("enhances release notes with game information", async () => {
      const mock = nock("https://api.github.com")
        .post("/app/installations/1/access_tokens")
        .reply(200, { token: "test" })
        .patch("/repos/Xaric23/DungeonCrawlerAI/releases/1", (body) => {
          expect(body.body).toContain("🎮 Play Now!");
          expect(body.body).toContain("https://xaric23.github.io/DungeonCrawlerAI/");
          expect(body.body).toContain("Quick Start");
          return true;
        })
        .reply(200, {});

      await probot.receive({
        name: "release.published",
        payload: releasePublishedPayload,
      });
      expect(mock.pendingMocks()).toStrictEqual([]);
    });

    test("handles release with null body", async () => {
      const nullBodyPayload = {
        ...releasePublishedPayload,
        release: {
          ...releasePublishedPayload.release,
          body: null,
        },
      };

      const mock = nock("https://api.github.com")
        .post("/app/installations/1/access_tokens")
        .reply(200, { token: "test" })
        .patch("/repos/Xaric23/DungeonCrawlerAI/releases/1", (body) => {
          expect(body.body).toContain("🎮 Play Now!");
          return true;
        })
        .reply(200, {});

      await probot.receive({
        name: "release.published",
        payload: nullBodyPayload,
      });
      expect(mock.pendingMocks()).toStrictEqual([]);
    });
  });
});
