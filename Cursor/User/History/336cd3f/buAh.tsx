import React from 'react';
import Fuse from 'fuse.js';
import {PastPaper, PrismaClient, Tag} from "@/src/generated/prisma";
import {redirect} from 'next/navigation';
import Pagination from '../../components/Pagination';
import PastPaperCard from '../../components/PastPaperCard';
import SearchBar from '../../components/SearchBar';
import UploadButtonPaper from '../../components/uploadButtonPaper';
import Dropdown from '../../components/FilterComponent';

const SCORE_THRESHOLD = 0.6;

type PastPaperWithTags = PastPaper & {
    tags: Tag[];
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

function performSearch(query: string, dataSet: PastPaperWithTags[]) {
    const options = {
        includeScore: true,
        keys: [
            { name: 'title', weight: 1 },
            { name: 'tags.name', weight: 2 }
        ],
        threshold: 0.4,
        ignoreLocation: true,
        minMatchCharLength: 2,
        findAllMatches: true,
        useExtendedSearch: true,
    };
    const fuse = new Fuse(dataSet, options);
    const searchResults = fuse.search({
        $or: [
            { title: query },
            { 'tags.name': query },
            { title: `'${query}` }
        ]
    });
    return searchResults
        .filter((fuseResult) => (fuseResult.score || 1) < SCORE_THRESHOLD)
        .map((fuseResult) => fuseResult.item);
}

async function pastPaperPage({ searchParams }: { searchParams: Promise<{ page?: string, search?: string, tags?: string | string[] }> }) {
    const pageSize = 9;
    const params = await searchParams;
    const search = params.search || '';
    const page = parseInt(params.page || '1', 10);
    const tags: string[] = Array.isArray(params.tags)
        ? params.tags
        : (params.tags ? params.tags.split(',') : []);

    // For development mode - return mock data if no database connection
    if (!process.env.DATABASE_URL) {
        const mockPastPapers = [
            {
                id: '1',
                title: 'Data Structures and Algorithms - CAT 1 2023',
                fileUrl: '#',
                thumbNailUrl: null,
                isClear: true,
                createdAt: new Date('2023-10-15'),
                updatedAt: new Date('2023-10-15'),
                authorId: 'dev-user',
                tags: [
                    { id: '1', name: 'CAT 1', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '2', name: 'A1', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '3', name: 'DSA', aliases: [], createdAt: new Date(), updatedAt: new Date() }
                ]
            },
            {
                id: '2',
                title: 'Computer Networks - CAT 2 2023',
                fileUrl: '#',
                thumbNailUrl: null,
                isClear: true,
                createdAt: new Date('2023-11-20'),
                updatedAt: new Date('2023-11-20'),
                authorId: 'dev-user',
                tags: [
                    { id: '4', name: 'CAT 2', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '5', name: 'B1', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '6', name: 'CN', aliases: [], createdAt: new Date(), updatedAt: new Date() }
                ]
            },
            {
                id: '3',
                title: 'Database Management Systems - FAT 2023',
                fileUrl: '#',
                thumbNailUrl: null,
                isClear: true,
                createdAt: new Date('2023-12-10'),
                updatedAt: new Date('2023-12-10'),
                authorId: 'dev-user',
                tags: [
                    { id: '7', name: 'FAT', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '8', name: 'C2', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '9', name: 'DBMS', aliases: [], createdAt: new Date(), updatedAt: new Date() }
                ]
            },
            {
                id: '4',
                title: 'Operating Systems - CAT 1 2022',
                fileUrl: '#',
                thumbNailUrl: null,
                isClear: true,
                createdAt: new Date('2022-10-12'),
                updatedAt: new Date('2022-10-12'),
                authorId: 'dev-user',
                tags: [
                    { id: '10', name: 'CAT 1', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '11', name: 'D2', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '12', name: 'OS', aliases: [], createdAt: new Date(), updatedAt: new Date() }
                ]
            },
            {
                id: '5',
                title: 'Machine Learning - CAT 2 2022',
                fileUrl: '#',
                thumbNailUrl: null,
                isClear: true,
                createdAt: new Date('2022-11-18'),
                updatedAt: new Date('2022-11-18'),
                authorId: 'dev-user',
                tags: [
                    { id: '13', name: 'CAT 2', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '14', name: 'E1', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '15', name: 'ML', aliases: [], createdAt: new Date(), updatedAt: new Date() }
                ]
            },
            {
                id: '6',
                title: 'Software Engineering - FAT 2022',
                fileUrl: '#',
                thumbNailUrl: null,
                isClear: true,
                createdAt: new Date('2022-12-05'),
                updatedAt: new Date('2022-12-05'),
                authorId: 'dev-user',
                tags: [
                    { id: '16', name: 'FAT', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '17', name: 'F1', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '18', name: 'SE', aliases: [], createdAt: new Date(), updatedAt: new Date() }
                ]
            },
            {
                id: '7',
                title: 'Artificial Intelligence - CAT 1 2024',
                fileUrl: '#',
                thumbNailUrl: null,
                isClear: true,
                createdAt: new Date('2024-01-15'),
                updatedAt: new Date('2024-01-15'),
                authorId: 'dev-user',
                tags: [
                    { id: '19', name: 'CAT 1', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '20', name: 'G2', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '21', name: 'AI', aliases: [], createdAt: new Date(), updatedAt: new Date() }
                ]
            },
            {
                id: '8',
                title: 'Web Development - CAT 2 2024',
                fileUrl: '#',
                thumbNailUrl: null,
                isClear: true,
                createdAt: new Date('2024-02-20'),
                updatedAt: new Date('2024-02-20'),
                authorId: 'dev-user',
                tags: [
                    { id: '22', name: 'CAT 2', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '23', name: 'A2', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '24', name: 'WD', aliases: [], createdAt: new Date(), updatedAt: new Date() }
                ]
            },
            {
                id: '9',
                title: 'Computer Graphics - FAT 2024',
                fileUrl: '#',
                thumbNailUrl: null,
                isClear: true,
                createdAt: new Date('2024-03-10'),
                updatedAt: new Date('2024-03-10'),
                authorId: 'dev-user',
                tags: [
                    { id: '25', name: 'FAT', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '26', name: 'B2', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '27', name: 'CG', aliases: [], createdAt: new Date(), updatedAt: new Date() }
                ]
            },
            {
                id: '10',
                title: 'Cybersecurity - CAT 1 2023',
                fileUrl: '#',
                thumbNailUrl: null,
                isClear: true,
                createdAt: new Date('2023-09-25'),
                updatedAt: new Date('2023-09-25'),
                authorId: 'dev-user',
                tags: [
                    { id: '28', name: 'CAT 1', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '29', name: 'C1', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '30', name: 'CS', aliases: [], createdAt: new Date(), updatedAt: new Date() }
                ]
            },
            {
                id: '11',
                title: 'Mobile App Development - CAT 2 2023',
                fileUrl: '#',
                thumbNailUrl: null,
                isClear: true,
                createdAt: new Date('2023-10-30'),
                updatedAt: new Date('2023-10-30'),
                authorId: 'dev-user',
                tags: [
                    { id: '31', name: 'CAT 2', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '32', name: 'D1', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '33', name: 'MAD', aliases: [], createdAt: new Date(), updatedAt: new Date() }
                ]
            },
            {
                id: '12',
                title: 'Cloud Computing - FAT 2023',
                fileUrl: '#',
                thumbNailUrl: null,
                isClear: true,
                createdAt: new Date('2023-12-15'),
                updatedAt: new Date('2023-12-15'),
                authorId: 'dev-user',
                tags: [
                    { id: '34', name: 'FAT', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '35', name: 'E2', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '36', name: 'CC', aliases: [], createdAt: new Date(), updatedAt: new Date() }
                ]
            },
            {
                id: '13',
                title: 'Blockchain Technology - CAT 1 2024',
                fileUrl: '#',
                thumbNailUrl: null,
                isClear: true,
                createdAt: new Date('2024-01-30'),
                updatedAt: new Date('2024-01-30'),
                authorId: 'dev-user',
                tags: [
                    { id: '37', name: 'CAT 1', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '38', name: 'F2', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '39', name: 'BT', aliases: [], createdAt: new Date(), updatedAt: new Date() }
                ]
            },
            {
                id: '14',
                title: 'Data Science - CAT 2 2024',
                fileUrl: '#',
                thumbNailUrl: null,
                isClear: true,
                createdAt: new Date('2024-02-25'),
                updatedAt: new Date('2024-02-25'),
                authorId: 'dev-user',
                tags: [
                    { id: '40', name: 'CAT 2', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '41', name: 'G1', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '42', name: 'DS', aliases: [], createdAt: new Date(), updatedAt: new Date() }
                ]
            },
            {
                id: '15',
                title: 'Internet of Things - FAT 2024',
                fileUrl: '#',
                thumbNailUrl: null,
                isClear: true,
                createdAt: new Date('2024-03-20'),
                updatedAt: new Date('2024-03-20'),
                authorId: 'dev-user',
                tags: [
                    { id: '43', name: 'FAT', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '44', name: 'A1', aliases: [], createdAt: new Date(), updatedAt: new Date() },
                    { id: '45', name: 'IoT', aliases: [], createdAt: new Date(), updatedAt: new Date() }
                ]
            }
        ];

        const filteredPastPapers = mockPastPapers.filter(paper => {
            if (tags.length === 0) return true;
            return tags.some(tag => paper.tags.some(paperTag => paperTag.name === tag));
        });

        const totalPages = Math.ceil(filteredPastPapers.length / pageSize);
        const paginatedPapers = filteredPastPapers.slice((page - 1) * pageSize, page * pageSize);
        const validatedPage = validatePage(page, totalPages);

        return (
            <div className="p-8 transition-colors flex flex-col min-h-screen items-center text-black dark:text-[#D5D5D5]">
                <h1 className="text-center mb-4">Past Papers (Development Mode)</h1>
                <div className="hidden w-5/6 lg:w-1/2 md:flex items-center justify-center p-4 space-y-4 sm:space-y-0 sm:space-x-4 pt-2">
                    <Dropdown pageType='past_papers' />
                    <SearchBar pageType="past_papers" initialQuery={search} />
                    <UploadButtonPaper />
                </div>

                <div className='flex-col w-5/6 md:hidden space-y-4'>
                    <SearchBar pageType="past_papers" initialQuery={search} />
                    <div className='flex justify-between'>
                        <Dropdown pageType='past_papers' />
                        <UploadButtonPaper />
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
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 justify-items-center">
                        {paginatedPapers.map((pastPaper, index) => (
                            <PastPaperCard key={pastPaper.id} pastPaper={pastPaper} index={index} />
                        ))}
                    </div>
                </div>

                <div className="mt-8">
                    <Pagination 
                        currentPage={validatedPage} 
                        totalPages={totalPages}
                        basePath="/past_papers"
                        searchQuery={search}
                        tagsQuery={tags.join(',')}
                    />
                </div>
            </div>
        );
    }

    const prisma = new PrismaClient();
    let filteredPastPapers = await prisma.pastPaper.findMany({
        where: {
            isClear: true,
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
            tags: true,
        },
        orderBy: {
            createdAt: 'desc',
        }
    });
    if (search) {
        filteredPastPapers = performSearch(search, filteredPastPapers);
    }

    const totalCount = filteredPastPapers.length;
    const totalPages = Math.ceil(totalCount / pageSize);

    const validatedPage = validatePage(page, totalPages);

    const startIndex = (validatedPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const paginatedPastPapers = filteredPastPapers.slice(startIndex, endIndex);

    if (validatedPage !== page) {
        const searchQuery = search ? `&search=${encodeURIComponent(search)}` : '';
        const tagsQuery = tags.length > 0 ? `&tags=${encodeURIComponent(tags.join(','))}` : '';
        redirect(`/past_papers?page=${validatedPage}${searchQuery}${tagsQuery}`);
    }

    return (
        <div className="p-8 transition-colors flex flex-col min-h-screen items-center text-black dark:text-[#D5D5D5]">
            <h1 className="text-center mb-4">Past Papers</h1>
            <div className="hidden w-5/6 lg:w-1/2 md:flex items-center justify-center p-4 space-y-4 sm:space-y-0 sm:space-x-4 pt-2">
                <Dropdown pageType='past_papers' />
                <SearchBar pageType="past_papers" initialQuery={search} />
                <UploadButtonPaper />
            </div>

            <div className='flex-col w-5/6 md:hidden space-y-4'>
                <SearchBar pageType="past_papers" initialQuery={search} />
                <div className='flex justify-between'>
                    <Dropdown pageType='past_papers' />
                    <UploadButtonPaper />
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
                <div className="w-fit grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 p-6  place-content-center">
                    {paginatedPastPapers.length > 0 ? (
                        paginatedPastPapers.map((eachPaper, index) => (
                            <div key={eachPaper.id} className="flex justify-center">
                                <PastPaperCard pastPaper={eachPaper} index={index} />
                            </div>
                        ))
                    ) : (
                        <p className="col-span-3 text-center">
                            {search || tags.length > 0
                                ? "No past papers found matching your search or selected tags."
                                : "No past papers found."}
                        </p>
                    )}
                </div>
            </div>
            {totalPages > 1 && (
                <div className="mt-4">
                    <Pagination
                        currentPage={validatedPage}
                        totalPages={totalPages}
                        basePath="/past_papers"
                        searchQuery={search}
                        tagsQuery={tags.join(',')}
                    />
                </div>
            )}
        </div>
    );
}

export default pastPaperPage;

