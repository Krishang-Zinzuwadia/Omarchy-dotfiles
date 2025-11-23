import React from 'react';
import Fuse from 'fuse.js';
import { Comment, ForumPost, PrismaClient, Tag, User, Vote } from "@/src/generated/prisma"
import { redirect } from 'next/navigation';
import Pagination from "../../components/Pagination";
import ForumCard from "../../components/ForumCard";
import SearchBar from "../../components/SearchBar";
import Dropdown from "../../components/FilterComponent";
import NewForumButton from "../../components/NewForumButton";
import { auth } from '@/app/auth';

const SCORE_THRESHOLD = 0.8;

type ForumPostWithDetails = ForumPost & {
  author: User;
  tags: Tag[];
  comments: (Comment & { author: User })[];
  votes: Vote[];
};

function validatePage(page: number, totalPages: number): number {
  if (isNaN(page) || page < 1) {
    return 1;
  }
  if (page > totalPages && totalPages > 0) {
    return totalPages;
  }
  return page;
}

function performSearch(query: string, dataSet: ForumPostWithDetails[]) {
  const options = {
    includeScore: true,
    keys: [
      { name: 'title', weight: 2 },
      { name: 'author.name', weight: 1 },
      { name: 'tags.name', weight: 1 },
      { name: 'description', weight: 1.5 },
      { name: 'comments.content', weight: 1 },
      { name: 'comments.author.name', weight: 0.5 }
    ],
    threshold: 0.7,
    ignoreLocation: true,
    minMatchCharLength: 2,
    findAllMatches: true,
    useExtendedSearch: true,
  };
  const fuse = new Fuse(dataSet, options);
  const searchResults = fuse.search({
    $or: [
      { title: query },
      { 'author.name': query },
      { 'tags.name': query },
      { description: query },
      { 'comments.content': query },
      { 'comments.author.name': query },
      { title: `'${query}` }
    ]
  });
  return searchResults
    .filter((fuseResult) => (fuseResult.score || 1) < SCORE_THRESHOLD)
    .map((fuseResult) => fuseResult.item);
}

async function forum({ searchParams }: { searchParams: Promise<{ page?: string, search?: string, tags?: string | string[] }> }) {
  const session = await auth();
  const currentUserId = session?.user?.id;
  const pageSize = 5;
  const params = await searchParams;
  const search = params.search || '';
  const page = parseInt(params.page || '1', 10);
  const tags: string[] = Array.isArray(params.tags)
    ? params.tags
    : (params.tags ? params.tags.split(',') : []);

  // For development mode - return mock data if no database connection
  if (!process.env.DATABASE_URL) {
    const mockForumPosts = [
      {
        id: '1',
        title: 'Sample Forum Post 1',
        description: 'This is a sample forum post for development mode.',
        upvoteCount: 5,
        downvoteCount: 1,
        createdAt: new Date(),
        updatedAt: new Date(),
        authorId: 'dev-user',
        forumId: 'dev-forum',
        tags: [
          { id: '1', name: 'CAT 1', aliases: [], createdAt: new Date(), updatedAt: new Date() },
          { id: '2', name: 'A1', aliases: [], createdAt: new Date(), updatedAt: new Date() }
        ],
        author: { id: 'dev-user', name: 'Development User', email: 'dev@example.com' },
        comments: [],
        votes: []
      },
      {
        id: '2',
        title: 'Sample Forum Post 2',
        description: 'Another sample forum post for testing.',
        upvoteCount: 3,
        downvoteCount: 0,
        createdAt: new Date(),
        updatedAt: new Date(),
        authorId: 'dev-user',
        forumId: 'dev-forum',
        tags: [
          { id: '3', name: 'FAT', aliases: [], createdAt: new Date(), updatedAt: new Date() },
          { id: '4', name: 'B2', aliases: [], createdAt: new Date(), updatedAt: new Date() }
        ],
        author: { id: 'dev-user', name: 'Development User', email: 'dev@example.com' },
        comments: [],
        votes: []
      }
    ];

    const filteredForumPosts = mockForumPosts.filter(post => {
      if (tags.length === 0) return true;
      return tags.some(tag => post.tags.some(postTag => postTag.name === tag));
    });

    const totalCount = filteredForumPosts.length;
    const totalPages = Math.ceil(totalCount / pageSize);
    const validatedPage = validatePage(page, totalPages);
    const startIndex = (validatedPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const paginatedPosts = filteredForumPosts.slice(startIndex, endIndex);

    return (
      <div className="p-8 transition-colors flex flex-col min-h-screen items-center text-black dark:text-[#D5D5D5]">
        <h1 className="text-center mb-4">Forum (Development Mode)</h1>
        <div className="hidden w-5/6 lg:w-1/2 md:flex items-center justify-center p-4 space-y-4 sm:space-y-0 sm:space-x-4 pt-2">
          <Dropdown pageType='forum' />
          <SearchBar pageType="forum" initialQuery={search} />
          <NewForumButton />
        </div>

        <div className='flex-col w-5/6 md:hidden space-y-4'>
          <SearchBar pageType="forum" initialQuery={search} />
          <div className='flex justify-between'>
            <Dropdown pageType='forum' />
            <NewForumButton />
          </div>
        </div>

        {tags.length > 0 && (
          <div className="flex justify-center mb-4">
            <div className="flex flex-wrap gap-2">
              {tags.map((tag, index) => (
                <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="flex justify-center">
          <div className="grid grid-cols-1 gap-4 justify-items-center">
            {paginatedPosts.length > 0 ? (
              paginatedPosts.map((post, index) => (
                <ForumCard
                  key={post.id}
                  post={post}
                  title={post.title}
                  desc={post.description}
                  author={post.author?.name || null}
                  createdAt={post.createdAt}
                  tags={post.tags}
                  comments={post.comments}
                />
              ))
            ) : (
              <p className="text-center">
                {search || tags.length > 0
                  ? "No forum posts found matching your search or selected tags."
                  : "No forum posts found."}
              </p>
            )}
          </div>
        </div>

        {totalPages > 1 && (
          <div className="mt-auto">
            <Pagination
              currentPage={validatedPage}
              totalPages={totalPages}
              basePath="/forum"
              searchQuery={search}
              tagsQuery={tags.join(',')}
            />
          </div>
        )}
      </div>
    );
  }

  const prisma = new PrismaClient();
  let filteredForumPosts = await prisma.forumPost.findMany({
    where: {
      ...(tags.length > 0 && {
        tags: {
          some: {
            name: {
              in: tags,
            },
          },
        },
      }),
    },
    include: {
      author: true,
      votes: {
        where: {
          userId: currentUserId
        }
      },
      tags: true,
      comments: {
        include: {
          author: true,
        },
      },
    },
    orderBy: {
      createdAt: 'desc'
    }
  });
  if (search) {
    filteredForumPosts = performSearch(search, filteredForumPosts);
  }

  const totalCount = filteredForumPosts.length;
  const totalPages = Math.ceil(totalCount / pageSize);

  const validatedPage = validatePage(page, totalPages);

  const startIndex = (validatedPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedForumPosts = filteredForumPosts.slice(startIndex, endIndex);

  if (validatedPage !== page) {
    const searchQuery = search ? `&search=${encodeURIComponent(search)}` : '';
    const tagsQuery = tags.length > 0 ? `&tags=${encodeURIComponent(tags.join(','))}` : '';
    redirect(`/forum?page=${validatedPage}${searchQuery}${tagsQuery}`);
  }

  return (
    <div className="transition-colors flex flex-col items-center min-h-screen text-black dark:text-[#D5D5D5] px-8 py-8">
      <h1 className="text-center mb-4">Forum</h1>

      <div className="hidden w-5/6 lg:w-1/2 md:flex items-center justify-center p-4 space-y-4 sm:space-y-0 sm:space-x-4 pt-2">
        <Dropdown pageType='forum' />
        <SearchBar pageType="forum" initialQuery={search} />
        <NewForumButton />
      </div>

      <div className='flex-col w-5/6 md:hidden space-y-4'>
        <SearchBar pageType="forum" initialQuery={search} />
        <div className='flex justify-between'>
          <Dropdown pageType='forum' />
          <NewForumButton />
        </div>
      </div>

      <div className="w-full mx-auto">
        {paginatedForumPosts.length > 0 ? (
          <div className="space-y-4">
            {paginatedForumPosts.map((eachPost) => (
              <ForumCard
                key={eachPost.id}
                title={eachPost.title}
                author={eachPost.author.name || 'Unknown'}
                desc={eachPost.description || 'No description available'}
                createdAt={eachPost.createdAt}
                tags={eachPost.tags}
                post={eachPost}
                comments={eachPost.comments}
              />
            ))}
          </div>
        ) : (
          <p className="text-center py-8">
            {search || tags.length > 0
              ? "No forum posts found matching your search or selected tags."
              : "No forum posts found."}
          </p>
        )}
      </div>

      {totalPages > 1 && (
        <div className="mt-auto">
          <Pagination
            currentPage={validatedPage}
            totalPages={totalPages}
            basePath="/forum"
            searchQuery={search}
            tagsQuery={tags.join(',')}
          />
        </div>
      )}
    </div>
  );
}

export default forum;
