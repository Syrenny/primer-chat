import { Button } from '@/components/ui/button'
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area'
import { Check, Copy } from 'lucide-react'
import { useTheme } from 'next-themes'
import { Highlight, themes } from 'prism-react-renderer'
import React, { useRef, useState } from 'react'

const CodeBlock = ({
	lang,
	codeChildren,
}: {
	lang: string
	codeChildren: string
}) => {
	const codeRef = useRef<HTMLPreElement | null>(null)
	const { resolvedTheme } = useTheme()
	const code = codeChildren.trimEnd()
	const theme = resolvedTheme === 'dark' ? themes.oneDark : themes.oneLight

	return (
		<div className='bg-muted rounded-md w-full max-w-full'>
			<CodeBar lang={lang} codeRef={codeRef} />
			<ScrollArea className='w-full max-w-full'>
				<Highlight code={code} language={lang} theme={theme}>
					{({
						className,
						style,
						tokens,
						getLineProps,
						getTokenProps,
					}) => (
						<pre
							ref={codeRef}
							className={`text-sm p-4 shrink contain-inline-size`}
							style={{
								...style,
								backgroundColor: 'transparent',
							}}
						>
							{tokens.map((line, i) => (
								<div key={i} {...getLineProps({ line })}>
									{line.map((token, key) => (
										<span
											key={key}
											{...getTokenProps({ token })}
										/>
									))}
								</div>
							))}
						</pre>
					)}
				</Highlight>
				<ScrollBar orientation='horizontal' />
			</ScrollArea>
		</div>
	)
}

const CodeBar = React.memo(
	({
		lang,
		codeRef,
	}: {
		lang: string
		codeRef: React.RefObject<HTMLPreElement | null>
	}) => {
		const [isCopied, setIsCopied] = useState<boolean>(false)

		const handleCopy = async () => {
			const codeString = codeRef.current?.textContent
			if (codeString) {
				await navigator.clipboard.writeText(codeString)
				setIsCopied(true)
				setTimeout(() => setIsCopied(false), 3000)
			}
		}

		return (
			<div className='flex items-center relative bg-secondary/50 px-4 py-1 text-xs font-sans'>
				<span className='text-sm'>{lang}</span>
				<Button
					variant='ghost'
					size='sm'
					className='ml-auto gap-1'
					onClick={handleCopy}
				>
					{isCopied ? (
						<>
							<Check className='w-4 h-4 text-muted-foreground text-sm' />
							Скопировано
						</>
					) : (
						<>
							<Copy className='w-4 h-4 text-muted-foreground not-only-of-type:text-sm' />
							Копировать
						</>
					)}
				</Button>
			</div>
		)
	}
)

CodeBar.displayName = 'CodeBar'

export default CodeBlock
